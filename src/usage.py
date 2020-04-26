import datetime
from utils.pivotal import Pivotal
from utils.print import get_printable_stories
from utils.slack import send_slack_message

project_id = 1234567
pivotal = Pivotal("mypivotaltoken")
# a week ago from today
week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
update_since = f"{week_ago:%m/%d/%Y}"

project = pivotal.get_project(project_id)
stories = pivotal.get_stories(project_id, update_since)
printable_stories = get_printable_stories(stories, pivotal.get_project_membership(project_id))

# compost slack message
slack_message = ""
for ps in printable_stories:
    slack_message += "%s\n\n" % ps

send_slack_message("myslacktoken", "#my_channel", slack_message)
