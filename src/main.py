import datetime
import os

from utils.pair_programming import get_pair_programming_message
from utils.pivotal import Pivotal
from utils.print import get_printable_stories, get_stories_count_recap, stories_count_per_type
from utils.slack import send_slack_message_blocks

# retrieve pivotal token from env variables
pivotal_token = os.getenv('PIVOTAL_TOKEN', "")
# retrieve the csv list of Pivotal project ids we want to print stories overview
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
        2449547,  # bonus vacanze
        2116794,  # io / api backend
        2088623,  # io / api per le PA
        2147248,  # io / developer & admin portal
        2431303,  # io / infrastructure
        2420220,  # io / integration
        2169201,  # io / io.italia.it
        2161158,  # io / pagopa proxy
        2463683,  # io / my portal
    ]
else:
    # use the list of projects ids provided in input
    project_ids = list(map(int, project_ids_csv.split(",")))

if len(slack_channel) < 0 <= len(slack_token):
    print('provide a valid Slack token in variable SLACK_TOKEN')
    exit(1)

days_before = 7
pivotal = Pivotal(pivotal_token)
# a week ago from today
week_ago = datetime.datetime.now() - datetime.timedelta(days=days_before)
update_since = f"{week_ago:%m/%d/%Y}"

shipped_stories_per_type = {}
rejected_stories_per_type = {}
project_no_stories = []
total_stories = 0
total_rejected_stories = 0
# a list of tuple: [(project,stories) ...]
project_and_stories = []
for project_id in project_ids:
    # retrieve project stories
    project = pivotal.get_project(project_id)
    all_stories = pivotal.get_stories(project_id, update_since, ["accepted","rejected"])
    accepted = list(filter(lambda s: s["current_state"] == "accepted",all_stories))
    rejected = list(filter(lambda s: s["current_state"] == "rejected",all_stories))
    project_and_stories.append((project, accepted))
    t, shipped_stories_per_type = stories_count_per_type(accepted,shipped_stories_per_type)
    total_stories += t
    t, rejected_stories_per_type = stories_count_per_type(rejected,rejected_stories_per_type)
    total_rejected_stories += t

if total_stories == 0:
    print("there are no accepted stories in the last %d days" % days_before)
    exit(0)

# compose the recap message
send_slack_message_blocks(slack_token, slack_channel, [
    {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": "Hello, I'm the Pivotal cat",
            "emoji": True
        },
        "image_url": "http://placekitten.com/200/200?image=%d" % (
                datetime.datetime.timestamp(datetime.datetime.now()) % 16),
        "alt_text": "Pivotal cat"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "In the last %d days we shipped *%d stories* (%s)" % (
                days_before, total_stories, get_stories_count_recap(shipped_stories_per_type))
        }
    },

])

if total_rejected_stories > 0:
    send_slack_message_blocks(slack_token, slack_channel, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*%d stories* are been *rejected* (%s)" % (
                    total_rejected_stories, get_stories_count_recap(rejected_stories_per_type))
            }
        },

    ])

for project, stories in project_and_stories:
    message_blocks = []
    project_id = project['id']
    if len(stories) == 0:
        project_no_stories.append(project_id)
        continue

    # get printable strings
    printable_stories = get_printable_stories(
        stories, pivotal.get_project_membership(project_id))
    total_stories, stories_per_type = stories_count_per_type(stories, {})
    message_blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*<https://www.pivotaltracker.com/n/projects/%d|%s>* (%d stories accepted: %s)\n" % (
                project['id'], project['name'], total_stories, get_stories_count_recap(stories_per_type))
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
        slice = 10
        count = 0
        while count <= len(message_blocks):
            send_slack_message_blocks(slack_token, slack_channel, message_blocks[count:count+slice])
            count += slice
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
        # send message to Slack channel if specified; print to stdout otherwise
        print(message_blocks)

### pair programming
pair_programming_message = get_pair_programming_message()
if len(slack_channel) > 0:
    send_slack_message_blocks(slack_token, slack_channel, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":desktop_computer::bulb::computer:" + pair_programming_message
                    }
                }
            ])


