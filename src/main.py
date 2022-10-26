#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from utils.env import days_span, github_company_repositories, GITHUB_COMPANY_NAME, slack_channel, slack_token
from utils.github2 import get_repo_stats2, group_by_state
from utils.slack import send_slack_message_blocks

end = datetime.datetime.now()
start = end - datetime.timedelta(days=days_span)
# it assumes that each item is a valid project inside {GITHUB_COMPANY_NAME} org
for github_project in github_company_repositories:
    pull_requests = get_repo_stats2(github_project, days_span)
    pull_requests_created = list(filter(lambda pr: (end - pr.created_at).days <= days_span, pull_requests))
    pull_requests_merged = list(filter(lambda pr: pr.merged, pull_requests))
    pull_requests_reviewed = list(filter(lambda pr: len(pr.reviewers), pull_requests))
    pull_requests_open_draft_closed = group_by_state(list(filter(lambda pr: pr.state in ["open","draft"], pull_requests)))
    repo_stats = " | ".join([f'{v} {k}' for k, v in pull_requests_open_draft_closed.items()])
    msg = f'These are the contributions included in *<https://github.com/{GITHUB_COMPANY_NAME}/{github_project}|{github_project.upper()}>* from *{start.day:02}/{start.month:02}* to *{end.day:02}/{end.month:02}*\n'
    if len(pull_requests_reviewed) > 0:
        for pr in pull_requests_reviewed:
            msg += f'- <{pr.url}|{pr.title.replace("`", "")}>'
            msg += "\n"
            if len(msg) > 2000:
                send_slack_message_blocks(slack_token, slack_channel, [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": msg
                        }
                    }
                ])
                msg = ""
        msg += "\n"
    msg += "*Pull requests stats*\n"
    msg += f'created: `{len(pull_requests)}`\n'
    msg += f'reviewed: `{len(pull_requests_reviewed)}`\n'
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
    break
    if (stats.total_pr_reviewed + stats.total_pr_created) == 0:
        continue
    # sort reviewer by contribution
    reviewers = sorted(stats.data.keys(),
                       key=lambda x: stats.data[x].pr_created_contribution + stats.data[x].pr_review_contribution,
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
        msg += f'PR reviewed contribution: {value.pr_review_contribution}\n'
        pr_reviewed_links = " - ".join(
            map(lambda pn: f'<https://github.com/{GITHUB_COMPANY_NAME}/{github_project}/pull/{pn}|#{pn}>',
                value.pr_reviewed))
        msg += f'PR reviewed: {len(value.pr_reviewed)} {pr_reviewed_links}\n'

        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'{header}```{msg}```'
                }
            }
        ], thread.data['ts'])
