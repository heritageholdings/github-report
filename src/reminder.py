import os

from utils.pair_programming import get_today_programming_pairs
from utils.slack import send_slack_message_blocks

SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'test_feed')
PAIR_PROGRAMMING_ENABLED = os.getenv('PAIR_PROGRAMMING_ENABLED', 'false').lower() == 'true'
WEEKLY_TEAM_REPORT_ENABLED = os.getenv('WEEKLY_TEAM_REPORT_ENABLED', 'true').lower() == 'true'

def send_reminder(msg: str):
	send_slack_message_blocks(SLACK_CHANNEL, [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": msg
			}
		}
	])


if PAIR_PROGRAMMING_ENABLED:
	pairs = get_today_programming_pairs()
	msg = '\n\n'
	if pairs:
		for pair in pairs:
			one, two = pair[0], pair[1]
			msg += f'- {one} - {two}\n'
		send_reminder(
			f":fire: :computer: Today from `15.30` to `16.30` we have the *<https://www.notion.so/heritageholdings/Pair-Programming-e60f0e144d6348d4a71d846be2963e69|Pair Programming>* sessions. \nDon't miss it, see you there!{msg}")


if WEEKLY_TEAM_REPORT_ENABLED:
	send_reminder(
		":bookmark: @here Hello tech team! In order to prepare our dones and todos for tomorrow’s *weekly team call*, we’d really appreciate it if you could *drop us a few lines about your past week* and future plans.\n\nDon’t be stingy, details are important! You can reply in this thread :point_right::skin-tone-2: :thread: ")