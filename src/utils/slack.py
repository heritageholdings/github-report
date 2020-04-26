import ssl
import certifi
from slack import WebClient
from slack.errors import SlackApiError


def send_slack_message(slack_token, channel, message):
    try:
        # avoid ssl certificate warning
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        slack_token = slack_token
        rtm_client = WebClient(
            token=slack_token, ssl=ssl_context
        )
        rtm_client.chat_postMessage(
            channel=channel,
            text=message)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
