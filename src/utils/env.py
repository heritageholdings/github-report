import os
GITHUB_TOKEN = os.getenv('GH_TOKEN', None)
slack_token = os.getenv('SLACK_TOKEN')
days_span = os.getenv('DAYS_SPAN', 7)
slack_channel = os.getenv('SLACK_CHANNEL', 'test_feed')
GITHUB_COMPANY_NAME = os.getenv('GH_COMPANY_NAME', 'heritageholdings')
github_company_repositories = list(
    map(lambda item: item.strip(), os.getenv('GH_COMPANY_REPOSITORIES', 'iconic').split(",")))
assert slack_token is not None