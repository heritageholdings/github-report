#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os

from utils.github import get_pull_requests_data, GithubStats
from utils.slack import send_slack_message_blocks

sdfsdf = os.getenv('GH_API_TOKEN')
slack_token = os.getenv('SLACK_TOKEN')
days_span = os.getenv('DAYS_SPAN', 7)
slack_channel = os.getenv('SLACK_CHANNEL', 'test_feed')
github_company_name = os.getenv('GH_COMPANY_NAME', 'heritageholdings')
github_company_repositories = os.getenv('GH_COMPANY_REPOSITORIES', ['iconic'])
assert slack_token is not None
assert sdfsdf is not None

end = datetime.datetime.now()
start = end - datetime.timedelta(days=days_span)
# it assumes that each item is a valid project inside {github_company_name} org
for github_project in github_company_repositories:
    repo_stats = " | ".join([f'{v} {k}' for k, v in GithubStats.get_repo_stats(github_project, sdfsdf).items()])
    pr_created = get_pull_requests_data(sdfsdf, github_project, start, end)
    pr_reviews = get_pull_requests_data(sdfsdf, github_project, start, end, 'closed', 'merged')
    stats = GithubStats(pr_created, pr_reviews)
    msg = f'These are the contributions included in *<https://github.com/{github_company_name}/{github_project}|{github_project.upper()}>* from *{start.day:02}/{start.month:02}* to *{end.day:02}/{end.month:02}*\n'
    if len(pr_reviews) > 0:
        msg += "*Contributions included during the period*\n"
        msg += '\n'.join(
            map(lambda pr: f'- <{pr.pr_data["html_url"]}|{pr.pr_data["title"].replace("`", "")}>', pr_reviews))
        msg += "\n"
    msg += "*Pull requests stats*\n"
    msg += f'created: `{stats.total_pr_created}`\n'
    msg += f'reviewed: `{stats.total_pr_reviewed}`\n'
    msg += f'current: `{repo_stats if len(repo_stats) else "all clear!"}`\n'
    thread = send_slack_message_blocks(slack_token, slack_channel, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        }
    ])
    if (stats.total_pr_reviewed + stats.total_pr_created) == 0:
        continue
    # sort reviewer by contribution
    reviewers = sorted(stats.data.keys(), key=lambda x: stats.data[x].pr_created_contribution + stats.data[x].pr_review_contribution,
                            reverse=True)
    if len(reviewers) > 0:
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '*Contributors stats*\n'
                }
            }
        ], thread.data['ts'])
    for developer in reviewers:
        value = stats.data[developer]
        header = f'`{developer}`\n'
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
