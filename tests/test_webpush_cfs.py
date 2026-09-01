# Copyright 2026 Collector Figures
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse

from sygnal.notifications import Device, Notification
from sygnal.webpushpushkin import WebpushPushkin


def test_cfs_minimal_payload_excludes_message_and_identity_data() -> None:
    raw = {
        "room_id": "!opaque-room:chat.collectorfigures.com",
        "room_name": "Private customer room",
        "room_alias": "#private:chat.collectorfigures.com",
        "event_id": "$opaque-event",
        "sender": "@public-id:chat.collectorfigures.com",
        "sender_display_name": "Customer Name",
        "type": "m.room.message",
        "content": {"msgtype": "m.text", "body": "private message body"},
        "counts": {"unread": 3, "missed_calls": 2},
        "devices": [
            {
                "app_id": "com.collectorfigures.chat.web",
                "pushkey": "p256dh",
                "data": {
                    "default_payload": {
                        "cfs_schema": 1,
                        "cfs_account_fingerprint": "ABCDEFGHIJKLMNOPQRSTUV",
                        "email": "must-not-pass@example.invalid",
                        "body": "must not pass",
                    }
                },
            }
        ],
    }
    notification = Notification(raw)
    payload = WebpushPushkin._build_cfs_minimal_payload(
        notification, notification.devices[0]
    )

    assert payload == {
        "cfs_schema": 1,
        "cfs_account_fingerprint": "ABCDEFGHIJKLMNOPQRSTUV",
        "room_id": "!opaque-room:chat.collectorfigures.com",
        "event_id": "$opaque-event",
        "unread": 3,
    }


def test_cfs_minimal_payload_rejects_unbounded_fingerprint() -> None:
    notification = Notification(
        {
            "event_id": "$event",
            "devices": [
                {
                    "app_id": "com.collectorfigures.chat.web",
                    "pushkey": "p256dh",
                }
            ],
        }
    )
    device = Device(
        {
            "app_id": "com.collectorfigures.chat.web",
            "pushkey": "p256dh",
            "data": {
                "default_payload": {
                    "cfs_schema": 1,
                    "cfs_account_fingerprint": "x" * 65,
                }
            },
        }
    )

    assert WebpushPushkin._build_cfs_minimal_payload(notification, device) == {
        "cfs_schema": 1,
        "event_id": "$event",
    }

    for fingerprint in ["A" * 21, "A" * 23, "A" * 21 + "+"]:
        device.data["default_payload"]["cfs_account_fingerprint"] = fingerprint
        assert WebpushPushkin._build_cfs_minimal_payload(notification, device) == {
            "cfs_schema": 1,
            "event_id": "$event",
        }


def test_pushkey_log_identifier_is_one_way_and_stable() -> None:
    identifier = WebpushPushkin._pushkey_log_id("sensitive-push-key")
    assert identifier == WebpushPushkin._pushkey_log_id("sensitive-push-key")
    assert identifier != "sensitive-push-key"
    assert len(identifier) == 12


def test_webpush_endpoint_validation_is_https_origin_safe_and_exact() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "cfs-webpush-endpoints.json"
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert (
        sha256(fixture_path.read_bytes()).hexdigest()
        == "a10840295981d1b2f66400a95ed92d2342d0988d259dc049086319d7180e700e"
    )

    assert fixtures["schema"] == "cfs-webpush-endpoint-fixtures/v2"
    assert fixtures["fixture_values"] == "synthetic_redactions"
    assert fixtures["real_browser_acceptance"] is False
    assert fixtures["safari_status"] == "fail_closed_pending_real_acceptance"
    assert set(fixtures["provenance"]) == {"chrome", "edge", "firefox"}

    for fixture in fixtures["valid"]:
        endpoint = fixture["endpoint"]
        assert (
            WebpushPushkin._validated_endpoint_domain(endpoint)
            == urlparse(endpoint).hostname
        )

    for fixture in fixtures["invalid"]:
        endpoint = fixture["endpoint"]
        try:
            WebpushPushkin._validated_endpoint_domain(endpoint)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"unsafe endpoint accepted ({fixture['reason']}): {endpoint}"
            )

    try:
        WebpushPushkin._validated_endpoint_domain(
            "https://db3.notify.windows.com/" + ("x" * 2048)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("overlong Windows endpoint accepted")
