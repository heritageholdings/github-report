#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from utils.env import DAYS_SPAN, GITHUB_COMPANY_REPOSITORIES, GITHUB_COMPANY_NAME, SLACK_CHANNEL, slack_token
from utils.github import get_pull_requests_recently_updated, group_by_state, group_by_developer, get_pull_requests
from utils.slack import send_slack_message_blocks

end = datetime.datetime.now()
start = end - datetime.timedelta(days=DAYS_SPAN)
# it assumes that each item is a valid project inside {GITHUB_COMPANY_NAME} org
for repository in GITHUB_COMPANY_REPOSITORIES:
    pull_requests = get_pull_requests_recently_updated(repository, DAYS_SPAN)
    by_state = group_by_state(pull_requests)
    pull_requests_created = list(filter(lambda pr: (end - pr.created_at).days <= DAYS_SPAN, pull_requests))

    msg = f'These are the contributions included in *<https://github.com/{GITHUB_COMPANY_NAME}/{repository}|{repository.upper()}>* from *{start.day:02}/{start.month:02}* to *{end.day:02}/{end.month:02}*\n'
    if len(by_state.reviewed) > 0:
        for pr in by_state.reviewed:
            msg += f'- <{pr.url}|{pr.title.replace("`", "")}>'
            msg += "\n"
            if len(msg) > 2000:
                send_slack_message_blocks(slack_token, SLACK_CHANNEL, [
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
    msg += f'reviewed: `{len(by_state.reviewed)}`\n'
    if len(by_state.closed):
        msg += f'closed: `{len(by_state.closed)}`\n'
    current_pull_requests_list = group_by_state(get_pull_requests(repository))
    current_pr_list = {"draft": current_pull_requests_list.draft, "open": current_pull_requests_list.open}
    # exclude from current those states that have no PRs
    repo_stats = " | ".join([f'{len(current_pr_list[k])} {k}' for k in filter(lambda k: len(current_pr_list[k]),
                                                                              current_pr_list)])
    msg += f'current: `{repo_stats if len(repo_stats) else "all clear!"}`\n'
    thread = send_slack_message_blocks(slack_token, SLACK_CHANNEL, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        }
    ])
    by_developer = group_by_developer(by_state.merged + by_state.open + by_state.draft)
    # sort reviewer by contribution
    reviewers = sorted(by_developer.keys(),
                       key=lambda x: by_developer[x].contribution + by_developer[x].review_contribution,
                       reverse=True)

    if len(by_developer) > 0:
        send_slack_message_blocks(slack_token, SLACK_CHANNEL, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '*Contributors stats*\n'
                }
            }
        ], thread.data['ts'])

        for developer_key in reviewers:
            developer_contribution = by_developer[developer_key]
            developer = developer_contribution.developer
            header = f'`<https://github.com/{developer.login_name}|@{developer.login_name}>{" (" + developer.name + ")" if developer.name else ""}`\n'
            msg = ''
            msg += f'PR created: {len(developer_contribution.pr_created)}\n'
            msg += f'PR created contribution: {developer_contribution.contribution}\n'
            msg += f'PR reviewed contribution: {developer_contribution.review_contribution}\n'
            pr_reviewed_links = " - ".join(
                map(lambda pn: f'<https://github.com/{GITHUB_COMPANY_NAME}/{repository}/pull/{pn}|#{pn}>',
                    developer_contribution.pr_reviewed))
            msg += f'PR reviewed: {len(developer_contribution.pr_reviewed)} {pr_reviewed_links}\n'

            send_slack_message_blocks(slack_token, SLACK_CHANNEL, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'{header}```{msg}```'
                    }
                }
            ], thread.data['ts'])
