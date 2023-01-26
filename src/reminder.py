import os
from utils.slack import send_slack_message_blocks

SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'test_feed')


def send_reminder(msg: str):
	send_slack_message_blocks("test_feed", [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": msg
			}
		}
	])

send_reminder("this is a simple test")