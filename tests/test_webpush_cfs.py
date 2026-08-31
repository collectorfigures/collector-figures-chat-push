# Copyright 2026 Collector Figures
#
# SPDX-License-Identifier: AGPL-3.0-only

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
                        "cfs_account_fingerprint": "opaque-fingerprint",
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
        "cfs_account_fingerprint": "opaque-fingerprint",
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


def test_pushkey_log_identifier_is_one_way_and_stable() -> None:
    identifier = WebpushPushkin._pushkey_log_id("sensitive-push-key")
    assert identifier == WebpushPushkin._pushkey_log_id("sensitive-push-key")
    assert identifier != "sensitive-push-key"
    assert len(identifier) == 12


def test_webpush_endpoint_validation_is_https_origin_safe_and_exact() -> None:
    assert (
        WebpushPushkin._validated_endpoint_domain(
            "https://fcm.googleapis.com/fcm/send/opaque"
        )
        == "fcm.googleapis.com"
    )

    for endpoint in [
        "http://fcm.googleapis.com/fcm/send/opaque",
        "https://user@fcm.googleapis.com/fcm/send/opaque",
        "https://fcm.googleapis.com:444/fcm/send/opaque",
        "https://fcm.googleapis.com/",
        "https://fcm.googleapis.com/fcm/send/opaque#fragment",
        "not-a-url",
    ]:
        try:
            WebpushPushkin._validated_endpoint_domain(endpoint)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe endpoint accepted: {endpoint}")
