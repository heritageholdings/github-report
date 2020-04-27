import datetime
import os
from utils.pivotal import Pivotal
from utils.print import get_printable_stories
from utils.slack import send_slack_message_blocks

# retrieve pivotal token from env variables
pivotal_token = os.getenv('PIVOTAL_TOKEN', "")
# retrive the csv list of Pivotal project ids we want to print stories overview
project_ids_csv = os.getenv('PIVOTAL_PROJECT_IDS', "")

# retrieve slack token from env variables (optional)
slack_token = os.getenv('SLACK_TOKEN', "")
# retrieve slack channel name to send reports from env variables
slack_channel = os.getenv('SLACK_CHANNEL', "#dev_io")

if len(pivotal_token) <= 0:
    print('provide a valid Pivotal token in variable PIVOTAL_TOKEN')
    exit(1)

if len(project_ids_csv) <= 0:
    # use the default list of projects if not specified
    project_ids = [
        2048617,  # io / app
        2116794,  # io / api backend
        2088623,  # io / api per le PA
        2147248,  # io / developer & admin portal
        2431303,  # io / infrastructure
        2420220,  # io / integration
        2169201,  # io / io.italia.it
        2161158   # io / pagopa proxy
    ]
else:
    # use the list of projects ids provided in input
    project_ids = list(map(int, project_ids_csv.split(",")))

if len(slack_channel) > 0 and len(slack_token) <= 0:
    print('provide a valid Slack token in variable SLACK_TOKEN')
    exit(1)

pivotal = Pivotal(pivotal_token)
# a week ago from today
week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
update_since = f"{week_ago:%m/%d/%Y}"

send_slack_message_blocks(slack_token, slack_channel, [
    {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": "Hello, I'm the Pivotal cat",
            "emoji": True
        },
        "image_url": "http://lorempixel.com/200/200/cats/?" + str(datetime.datetime.now()),
        "alt_text": "Pivotal cat"
    },
    {
        "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Here's what has been shipped during the last 7 days."
                }
    },
])

project_no_stories = []

for project_id in project_ids:
    message_blocks = []
    # retrieve project stories
    project = pivotal.get_project(project_id)
    stories = pivotal.get_stories(project_id, update_since)
    if len(stories) == 0:
        project_no_stories.append(project_id)
        continue
    # get printable strings
    printable_stories = get_printable_stories(
        stories, pivotal.get_project_membership(project_id))
    message_blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*<https://www.pivotaltracker.com/n/projects/%d|%s>* (%d stories accepted)\n" % (
                project['id'], project['name'], len(printable_stories))
        }
    })

    # compose slack message
    for ps in printable_stories:
        message_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "%s\n\n" % ps
            }
        })

    message_blocks.append({
        "type": "divider"
    })

    if len(slack_channel) > 0:
        send_slack_message_blocks(slack_token, slack_channel, message_blocks)
    else:
        print(message_blocks)

if len(project_no_stories) > 0:
    parts = []
    for project_id in project_no_stories:
        project = pivotal.get_project(project_id)
        parts.append("*<https://www.pivotaltracker.com/n/projects/%d|%s>*" % (
            project['id'], project['name']))
    if len(slack_channel) > 0:
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "❗️ No stories accepted for " + ", ".join(parts)
                }
            }
        ])
    else:
        print(message_blocks)


# send message to Slack channel if specified; print to stdout otherwise
