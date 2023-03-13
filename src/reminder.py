import os

from utils.pair_programming import get_today_programming_pairs
from utils.slack import send_slack_message_blocks

SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'test_feed')


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


pairs = get_today_programming_pairs()
msg = ''
if pairs:
	msg += f'\n\n:busts_in_silhouette:\n'
	for pair in pairs:
		msg += f'- {pair[0]} and {pair[1]}\n'
	send_reminder(
		f":fire: :computer: Today from `15.30` to `16.30` we have the *<https://www.notion.so/heritageholdings/Pair-Programming-e60f0e144d6348d4a71d846be2963e69|Pair Programming>* sessions. Don't miss it, see you there!{msg}")
