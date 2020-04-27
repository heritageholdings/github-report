import datetime
import os
from utils.pivotal import Pivotal
from utils.print import get_printable_stories
from utils.slack import send_slack_message

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
    project_ids = [2048617,  # io / app
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
    # send message to Slack channel if specified; print to stdout otherwise
    if len(slack_channel) > 0:
        send_slack_message(slack_token, slack_channel, slack_message)
        send_slack_message(slack_token, slack_channel, "#" * 25)
    else: 
        print(slack_message)
        print("#" * 25)

for project_id in project_no_stories:
    project = pivotal.get_project(project_id)
    slack_message = "*<https://www.pivotaltracker.com/n/projects/%d|%s>*\n" % (project['id'], project['name'])
    
    if len(slack_channel) > 0:
        send_slack_message(slack_token, slack_channel, slack_message)
        send_slack_message(slack_token, slack_channel, "*no stories*")
        send_slack_message(slack_token, slack_channel, "#" * 25)
    else: 
        print(slack_message)
        print("*no stories*")
        print("#" * 25)
