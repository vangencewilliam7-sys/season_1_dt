"""
skills/base/notify_skill.py

BaseSkill — Send Notification / Message
SRP: One job — send a notification (email, SMS, in-app). No expert context.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.interfaces.skill import BaseSkill, SkillParams, SkillResult


class NotifySkill(BaseSkill):
    """
    Raw capability: send a notification or message.

    In MVP, this logs the notification (no real email sending infra yet).
    Replace the _send() method with an SMTP/SendGrid/Twilio call when ready.

    Input params:
        channel     : str   — "email" | "sms" | "in_app" | "slack"
        recipient   : str   — email address / phone / user ID
        subject     : str   — subject line (for email)
        body        : str   — notification body content
        priority    : str   — "normal" | "urgent"
    """

    def get_skill_id(self) -> str:
        return "send_notification"

    def get_description(self) -> str:
        return "Send a notification or message through a specified channel."

    def execute(self, params: SkillParams) -> SkillResult:
        try:
            p = params.raw_params
            channel = p.get("channel", "email")
            recipient = p.get("recipient", "unknown")
            subject = p.get("subject", "Notification")
            body = p.get("body", "")
            priority = p.get("priority", "normal")

            # MVP: log it. Replace with real transport.
            result = self._send(channel, recipient, subject, body, priority)

            return SkillResult(
                success=True,
                output=result,
                skill_id=self.get_skill_id(),
                metadata={
                    "channel": channel,
                    "recipient": recipient,
                    "priority": priority,
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                skill_id=self.get_skill_id(),
                error_message=str(e),
            )

    def _send(self, channel: str, recipient: str, subject: str, body: str, priority: str) -> dict:
        """
        MVP: simulate sending. Replace with real transport adapter.
        Returns a delivery receipt dict.
        """
        print(f"[NotifySkill] MOCK SEND via {channel}")
        print(f"  To:       {recipient}")
        print(f"  Subject:  {subject}")
        print(f"  Priority: {priority}")
        print(f"  Body:\n{body}")
        return {
            "status": "sent (mock)",
            "channel": channel,
            "recipient": recipient,
            "subject": subject,
        }
