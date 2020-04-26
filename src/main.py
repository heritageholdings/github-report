import datetime
import os
from utils.pivotal import Pivotal
from utils.print import get_printable_stories
from utils.slack import send_slack_message

# retrieve pivotal token from env variables
pivotal_token = os.getenv('PIVOTAL_TOKEN', "")
# retrieve slack token from env variables
slack_token = os.getenv('SLACK_TOKEN', "")

if 0 in (len(pivotal_token), len(slack_token)):
    print('provide a valid token in slack/pivotal.token file')
    exit(1)

# slack channel to send reports
slack_channel = "#dev_io"
# define all project ids we want to print stories overview
project_ids = [2048617,  # io / app
               2116794,  # io / api backend
               2088623,  # io / api per le PA
               2147248,  # io / developer & admin portal
               2325988,  # io / infrastructure
               2420220,  # io / integration
               2169201,  # io / io.italia.it
               2161158,  # io / pagopa proxy
               ]

pivotal = Pivotal(pivotal_token)
# a week ago from today
week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
update_since = f"{week_ago:%m/%d/%Y}"
project_no_stories = []
for project_id in project_ids:
    # retrieve project stories
    project = pivotal.get_project(project_id)
    stories = pivotal.get_stories(project_id, update_since)
    if len(stories) == 0:
        project_no_stories.append(project_id)
        continue
    # get printable strings
    printable_stories = get_printable_stories(stories, pivotal.get_project_membership(project_id))
    slack_message = "*<https://www.pivotaltracker.com/n/projects/%d|%s>*\n" % (project['id'], project['name'])
    # compose slack message
    for ps in printable_stories:
        slack_message += "%s\n\n" % ps
    slack_message += "\n\n"
    send_slack_message(slack_token, slack_channel, slack_message)
    send_slack_message(slack_token, slack_channel, "#" * 25)

for project_id in project_no_stories:
    project = pivotal.get_project(project_id)
    slack_message = "*<https://www.pivotaltracker.com/n/projects/%d|%s>*\n" % (project['id'], project['name'])
    send_slack_message(slack_token, slack_channel, slack_message)
    send_slack_message(slack_token, slack_channel, "*no stories*")
    send_slack_message(slack_token, slack_channel, "#" * 25)
