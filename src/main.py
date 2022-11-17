#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from utils.env import DAYS_SPAN, GITHUB_COMPANY_REPOSITORIES, GITHUB_COMPANY_NAME, SLACK_CHANNEL
from utils.github import get_pull_requests_recently_updated, group_by_state, group_by_developer, get_pull_requests, \
    get_pull_requests_recently_created, group_by_type
from utils.slack import send_slack_message_blocks

end = datetime.datetime.now()
start = end - datetime.timedelta(days=DAYS_SPAN)
# it assumes each item is an existing repository inside {GITHUB_COMPANY_NAME} organization
for repository in GITHUB_COMPANY_REPOSITORIES:
    pull_requests_recently_updated = get_pull_requests_recently_updated(repository, DAYS_SPAN)
    by_state = group_by_state(pull_requests_recently_updated)
    pull_requests_created = get_pull_requests_recently_created(repository, DAYS_SPAN)

    msg = f'These are the stats about *<https://github.com/{GITHUB_COMPANY_NAME}/{repository}|{repository.upper()}>* repository from *{start.day:02}/{start.month:02}* to *{end.day:02}/{end.month:02}*\n'
    msg += "*Pull requests stats*\n"
    msg += f'`{len(pull_requests_created)}` _created_\n'
    msg += f'`{len(by_state.merged)}` _merged_ (`{len(by_state.reviewed)}` _reviewed_)\n'
    if len(by_state.closed):
        msg += f'`{len(by_state.closed)}` _closed_\n'
    current_pull_requests_list = group_by_state(get_pull_requests(repository))
    current_pr_list = {"draft": current_pull_requests_list.draft, "open": current_pull_requests_list.open}
    # exclude from current those states that have no PRs
    repo_stats = " & ".join([f'{len(current_pr_list[k])} {k}' for k in filter(lambda k: len(current_pr_list[k]) > 0,
                                                                              current_pr_list)])
    by_type = group_by_type(by_state.merged)
    msg += " | ".join(f'`{k}: {len(v)}`' for k, v in by_type.items()) + "\n"
    msg += f'current `{repo_stats if len(repo_stats) else "all clear!"}`\n'

    thread = send_slack_message_blocks(SLACK_CHANNEL, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        }
    ])
    msg = ""
    if len(by_state.merged) > 0:
        msg += "*PR merged list*\n"
        for pr in by_state.merged:
            msg += f'- <{pr.url}|{pr.title.replace("`", "")}>'
            msg += "\n"
            if len(msg) > 2000:
                # avoid exceeding payload size
                send_slack_message_blocks(SLACK_CHANNEL, [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": msg
                        }
                    }
                ], thread.data['ts'])
                msg = ""
        msg += "\n"
    thread = send_slack_message_blocks(SLACK_CHANNEL, [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        }
    ], thread.data['ts'])
    by_developer = group_by_developer(by_state.merged + by_state.open + by_state.draft)
    # sort reviewer by contribution
    reviewers = sorted(by_developer.keys(),
                       key=lambda x: by_developer[x].contribution + by_developer[x].review_contribution,
                       reverse=True)

    if len(by_developer) > 0:
        send_slack_message_blocks(SLACK_CHANNEL, [
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
            header = f'`@{developer.login_name}{" (" + developer.name + ")" if developer.name else ""}`\n'
            msg = ''
            msg += f'PR created: {len(developer_contribution.pr_created)}\n'
            pr_reviewed_links = " - ".join(
                map(lambda pn: f'<https://github.com/{GITHUB_COMPANY_NAME}/{repository}/pull/{pn}|#{pn}>',
                    developer_contribution.pr_reviewed))
            msg += f'PR reviewed: {len(developer_contribution.pr_reviewed)} {"(" + pr_reviewed_links + ")" if len(pr_reviewed_links) else ""}\n'
            msg += f'PR created contribution: {developer_contribution.contribution}\n'
            msg += f'PR reviewed contribution: {developer_contribution.review_contribution}\n'

            send_slack_message_blocks(SLACK_CHANNEL, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f'{header}```{msg}```'
                    }
                }
            ], thread.data['ts'])
