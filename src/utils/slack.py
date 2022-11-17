import ssl
import certifi
from slack import WebClient
from slack.errors import SlackApiError

from utils.env import SLACK_TOKEN


def send_slack_message(channel, message):
    try:
        # avoid ssl certificate warning
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        rtm_client = WebClient(
            token=SLACK_TOKEN, ssl=ssl_context
        )
        rtm_client.chat_postMessage(
            channel=channel,
            text=message)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


def send_slack_message_blocks(channel, blocks, thread_ts=None):
    try:
        # avoid ssl certificate warning
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        rtm_client = WebClient(
            token=SLACK_TOKEN, ssl=ssl_context
        )
        return rtm_client.chat_postMessage(
            thread_ts=thread_ts,
            channel=channel,
            blocks=blocks)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")
