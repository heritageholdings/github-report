#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os

from utils.github import get_pull_requests_data, GithubStats, get_reviewer_description
from utils.slack import send_slack_message_blocks

github_token = os.getenv('GITHUB_TOKEN')
slack_token = os.getenv('SLACK_TOKEN')
days_span = os.getenv('DAYS_SPAN', 7)
slack_channel = os.getenv('SLACK_CHANNEL', 'test_feed')
github_company_name = os.getenv('GITHUB_COMPANY_NAME', 'heritageholdings')
assert github_company_name is not None
assert github_token is not None

# github stats
end = datetime.datetime.now()
start = end - datetime.timedelta(days=days_span)
# it assumes that each item is a valid project inside heritageholdings org (https://github.com/heritageholdings)
stats_for_projects = ['iconic']
for project in stats_for_projects:
    repo_stats = " | ".join([f'{v} {k}' for k, v in GithubStats.get_repo_stats(project, github_token).items()])
    pr_created = get_pull_requests_data(github_token, project, start, end)
    pr_reviews = get_pull_requests_data(github_token, project, start, end, 'closed', 'merged')
    stats = GithubStats(pr_created, pr_reviews)
    msg = f'*<https://github.com/{github_company_name}/{project}|{project.upper()}>* repo stats\n\n'
    msg += f':thermometer: status `{repo_stats if len(repo_stats) else "all clear!"}`\n'
    msg += f':heavy_plus_sign: PR created `{stats.total_pr_created}`\n'
    msg += f':memo: PR reviewed `{stats.total_pr_reviewed}`\n'
    thread = send_slack_message_blocks(slack_token, slack_channel, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        }
    ])
    pr_reviews_details = f'These are the contributions included in _{project}_ in the last {days_span} days'
    pr_reviews_details += '\n'.join(map(lambda pr: f'- <{pr.pr_data["html_url"]}|{pr.pr_data["title"]}>', pr_reviews))
    if (stats.total_pr_reviewed + stats.total_pr_created) == 0:
        continue
    # put not reviewer at the end
    reviewers = stats.data.keys()
    for developer in reviewers:
        value = stats.data[developer]
        header = f'{developer}\n'
        msg = ''
        msg += f'PR created: {value.pr_created_count}\n'
        msg += f'PR created contribution: {value.pr_created_contribution}\n'
        msg += f'PR reviewed: {value.pr_review_count}\n'
        msg += f'PR reviewed contribution: {value.pr_review_contribution}\n'
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'{header}```{msg}```'
                }
            }
        ], thread.data['ts'])
