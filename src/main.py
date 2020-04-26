import datetime
from os.path import join, dirname
from utils.pivotal import Pivotal
from utils.print import get_printable_stories
from utils.slack import send_slack_message

# store your token in pivotal.token file as plain text
pivotal_token = ""
# store your token in slack.token file as plain text
slack_token = ""
try:
    with open(join(dirname(__file__), 'pivotal.token'), 'r') as f:
        pivotal_token = f.read()

    with open(join(dirname(__file__), 'slack.token'), 'r') as f:
        slack_token = f.read()
except Exception as ex:
    print(ex)
    exit(1)

if 0 in (len(pivotal_token), len(slack_token)):
    print('provide a valid token in slack/pivotal.token file')
    exit(1)

# slack channel to send reports
slack_channel = "#io_status"
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
for project_id in project_ids:
    # retrieve project stories
    project = pivotal.get_project(project_id)
    stories = pivotal.get_stories(project_id, update_since)
    if len(stories) == 0:
        continue
    # get printable strings
    printable_stories = get_printable_stories(stories, pivotal.get_project_membership(project_id))
    slack_message = "*<https://www.pivotaltracker.com/n/projects/%d|%s>*\n" % (project['id'], project['name'])
    # compose slack message
    for ps in printable_stories:
        slack_message += "%s\n\n" % ps
    slack_message += "\n\n"
    send_slack_message(slack_token, slack_channel, slack_message)
