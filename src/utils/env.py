import os
GITHUB_TOKEN = os.getenv('GH_TOKEN', None)
SLACK_TOKEN = os.getenv('SLACK_TOKEN', None)
DAYS_SPAN = os.getenv('DAYS_SPAN', 7)
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'test_feed')
GITHUB_COMPANY_NAME = os.getenv('GH_COMPANY_NAME', 'heritageholdings')
GITHUB_COMPANY_REPOSITORIES = list(
    map(lambda item: item.strip(), os.getenv('GH_COMPANY_REPOSITORIES', 'iconic').split(",")))

assert SLACK_TOKEN is not None, "Slack token cannot be null"
