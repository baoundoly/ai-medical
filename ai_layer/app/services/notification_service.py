"""
Notification service — stub implementation.
In production, wire to email (SendGrid/SES), SMS (Twilio/BDApps), push notifications.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationChannel:
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


def send_notification(
    recipient_id: int,
    title: str,
    body: str,
    channel: str = NotificationChannel.IN_APP,
    data: Optional[dict] = None,
) -> dict:
    """Send a notification to a user. Stub — logs to console."""
    payload = {
        "recipient_id": recipient_id,
        "title": title,
        "channel": channel,
        "data": data or {},
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "sent",
    }
    # TODO: replace with real delivery mechanism (email/SMS/push)
    logger.info("[NOTIFICATION] %s → %s", channel.upper(), title)
    return payload


def send_critical_lab_alert(
    doctor_id: int,
    patient_name: str,
    test_name: str,
    value: str,
) -> dict:
    """Send a critical lab result alert to the attending doctor."""
    return send_notification(
        recipient_id=doctor_id,
        title="⚠️ Critical Lab Result",
        body=f"Patient {patient_name}: {test_name} = {value} (CRITICAL)",
        channel=NotificationChannel.PUSH,
        data={"type": "critical_lab"},
    )


def send_appointment_reminder(patient_id: int, appointment_time: str, doctor_name: str) -> dict:
    """Send appointment reminder to patient."""
    return send_notification(
        recipient_id=patient_id,
        title="Appointment Reminder",
        body=f"Your appointment with Dr. {doctor_name} is at {appointment_time}.",
        channel=NotificationChannel.SMS,
        data={"type": "appointment_reminder"},
    )


def send_prescription_ready(patient_id: int) -> dict:
    """Notify patient that their prescription is ready for collection."""
    return send_notification(
        recipient_id=patient_id,
        title="Prescription Ready",
        body="Your prescription has been signed and is ready for dispensing.",
        channel=NotificationChannel.IN_APP,
        data={"type": "prescription_ready"},
    )
