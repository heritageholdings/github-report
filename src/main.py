#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from utils.env import days_span, github_company_repositories, GITHUB_COMPANY_NAME, slack_channel, slack_token
from utils.github2 import get_repo_stats2, group_by_state, group_by_developer
from utils.slack import send_slack_message_blocks

end = datetime.datetime.now()
start = end - datetime.timedelta(days=days_span)
# it assumes that each item is a valid project inside {GITHUB_COMPANY_NAME} org
for repository in github_company_repositories:
    pull_requests = get_repo_stats2(repository, days_span)
    by_state = group_by_state(pull_requests)
    pull_requests_created = list(filter(lambda pr: (end - pr.created_at).days <= days_span, pull_requests))

    msg = f'These are the contributions included in *<https://github.com/{GITHUB_COMPANY_NAME}/{repository}|{repository.upper()}>* from *{start.day:02}/{start.month:02}* to *{end.day:02}/{end.month:02}*\n'
    if len(by_state.reviewed) > 0:
        for pr in by_state.reviewed:
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
    msg += f'reviewed: `{len(by_state.reviewed)}`\n'
    if len(by_state.closed):
        msg += f'closed: `{len(by_state.closed)}`\n'
    open_draft_closed = {"draft": by_state.draft, "open": by_state.open}
    # exclude from current those states that have no PRs
    repo_stats = " | ".join([f'{len(open_draft_closed[k])} {k}' for k in filter(lambda k: len(open_draft_closed[k]),
                                                                                open_draft_closed)])
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
    by_developer = group_by_developer(by_state.merged + by_state.open)
    # sort reviewer by contribution
    reviewers = sorted(by_developer.keys(),
                       key=lambda x: by_developer[x].contribution + by_developer[x].review_contribution,
                       reverse=True)

    if len(by_developer) > 0:
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": '*Contributors stats*\n'
                }
            }
        ], thread.data['ts'])

        for developer_contribution in by_developer.values():
            developer = developer_contribution.developer
            header = f'`{developer.name if developer.name else "n/a"} (@{developer.login_name})`\n'
            msg = ''
            msg += f'PR created: {len(developer_contribution.pr_created)}\n'
            msg += f'PR created contribution: {developer_contribution.contribution}\n'
            msg += f'PR reviewed contribution: {developer_contribution.review_contribution}\n'
            pr_reviewed_links = " - ".join(
                map(lambda pn: f'<https://github.com/{GITHUB_COMPANY_NAME}/{repository}/pull/{pn}|#{pn}>',
                    developer_contribution.pr_reviewed))
            msg += f'PR reviewed: {len(developer_contribution.pr_reviewed)} {pr_reviewed_links}\n'

            send_slack_message_blocks(slack_token, slack_channel, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'{header}```{msg}```'
                    }
                }
            ], thread.data['ts'])
