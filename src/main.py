#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os

from utils.github import get_pull_requests_data, GithubStats, get_reviewer_description
from utils.pair_programming import get_pair_programming_message
from utils.pivotal import Pivotal
from utils.print import get_printable_stories, get_stories_count_recap, stories_count_per_type
from utils.slack import send_slack_message_blocks

# retrieve pivotal token from env variables
pivotal_token = os.getenv('PIVOTAL_TOKEN', "")
# retrieve the csv list of Pivotal project ids we want to print stories overview
project_ids_csv = os.getenv('PIVOTAL_PROJECT_IDS', "")

# retrieve slack token from env variables (optional)
slack_token = os.getenv('SLACK_TOKEN', "")
# slack channel name to send reports
slack_channel = os.getenv('SLACK_CHANNEL', "#dev_io")
# slack channel name to send pr stats report
pr_stats_slack_channel = os.getenv('SLACK_CHANNEL_PR_STATS', "#io_dev_app_feed")
# retrieve github token from env variables (optional)
github_token = os.getenv('GITHUB_TOKEN', None)

# configuration class
class Config():
    # if true, it will be reported also these projects for which no stories are been completed
    print_project_with_no_stories = os.getenv('REPORT_PROJECTS_NO_STORIES', False)
    # if true, it will be evaluated pivotal projects stats
    evaluate_pivotal_projects = os.getenv('EVALUATE_PIVOTAL_PROJECTS', False)
    # if true, it will be reported pairs for pair programming
    evaluate_pair_programming = os.getenv('EVALUATE_PAIR_PROGRAMMING', True)
    # if true, it will be evaluated PR stats
    evaluate_pr_stats = os.getenv('EVALUATE_PR_STATS', True)

if len(pivotal_token) <= 0:
    print('provide a valid Pivotal token in variable PIVOTAL_TOKEN')
    exit(1)

if len(project_ids_csv) <= 0:
    # use the default list of projects if not specified
    project_ids = [
        2048617,  # io / app
        2449547,  # bonus vacanze
        2116794,  # io / api backend
        2088623,  # io / api per le PA
        2147248,  # io / developer & admin portal
        2431303,  # io / infrastructure
        2420220,  # io / integration
        2169201,  # io / io.italia.it
        2161158,  # io / pagopa proxy
        2463683,  # io / my portal
        2477137,  # io / cashback
        2477115,  # io / pay,
        2477157,  # io / autenticazione e profilo
        2476636,  # io / carta nazionale giovani
    ]
else:
    # use the list of projects ids provided in input
    project_ids = list(map(int, project_ids_csv.split(",")))

if len(slack_channel) < 0 <= len(slack_token):
    print('provide a valid Slack token in variable SLACK_TOKEN')
    exit(1)

if Config.evaluate_pivotal_projects:
    days_before = 7
    pivotal = Pivotal(pivotal_token)
    # a week ago from today
    week_ago = datetime.datetime.now() - datetime.timedelta(days=days_before)
    update_since = f"{week_ago:%m/%d/%Y}"

    shipped_stories_per_type = {}
    rejected_stories_per_type = {}
    project_no_stories = []
    total_stories = 0
    total_rejected_stories = 0
    # a list of tuple: [(project,stories) ...]
    project_and_stories = []
    for project_id in project_ids:
        # retrieve project stories
        project = pivotal.get_project(project_id)
        all_stories = pivotal.get_stories(project_id, update_since, ["accepted", "rejected"])
        accepted = list(filter(lambda s: s["current_state"] == "accepted", all_stories))
        rejected = list(filter(lambda s: s["current_state"] == "rejected", all_stories))
        project_and_stories.append((project, accepted))
        t, shipped_stories_per_type = stories_count_per_type(accepted, shipped_stories_per_type)
        total_stories += t
        t, rejected_stories_per_type = stories_count_per_type(rejected, rejected_stories_per_type)
        total_rejected_stories += t

    if total_stories == 0:
        print("there are no accepted stories in the last %d days" % days_before)

    # compose the recap message
    send_slack_message_blocks(slack_token, slack_channel, [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "Hello, I'm the Pivotal cat",
                "emoji": True
            },
            "image_url": "http://placekitten.com/200/200?image=%d" % (
                    datetime.datetime.timestamp(datetime.datetime.now()) % 16),
            "alt_text": "Pivotal cat"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "In the last %d days we shipped *%d stories* (%s)" % (
                    days_before, total_stories, get_stories_count_recap(shipped_stories_per_type))
            }
        },

    ])

    if total_rejected_stories > 0:
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*%d stories* are been *rejected* (%s)" % (
                        total_rejected_stories, get_stories_count_recap(rejected_stories_per_type))
                }
            },

        ])

    for project, stories in project_and_stories:
        message_blocks = []
        project_id = project['id']
        if len(stories) == 0:
            project_no_stories.append(project_id)
            continue

        # get printable strings
        printable_stories = get_printable_stories(
            stories, pivotal.get_project_membership(project_id))
        total_stories, stories_per_type = stories_count_per_type(stories, {})
        message_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*<https://www.pivotaltracker.com/n/projects/%d|%s>* (%d stories accepted: %s)\n" % (
                    project['id'], project['name'], total_stories, get_stories_count_recap(stories_per_type))
            }
        })

        # compose slack message
        for ps in printable_stories:
            message_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "%s\n\n" % ps
                }
            })

        message_blocks.append({
            "type": "divider"
        })

        if len(slack_channel) > 0:
            slice = 10
            count = 0
            while count <= len(message_blocks):
                send_slack_message_blocks(slack_token, slack_channel, message_blocks[count:count + slice])
                count += slice
        else:
            print(message_blocks)

    if Config.print_project_with_no_stories and len(project_no_stories) > 0:
        parts = []
        for project_id in project_no_stories:
            project = pivotal.get_project(project_id)
            parts.append("*<https://www.pivotaltracker.com/n/projects/%d|%s>*" % (
                project['id'], project['name']))
        if len(slack_channel) > 0:
            send_slack_message_blocks(slack_token, slack_channel, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "❗️ No stories accepted for\n" + "\n".join(parts)
                    }
                }
            ])
        else:
            # send message to Slack channel if specified; print to stdout otherwise
            print(message_blocks)

### pair programming
if Config.evaluate_pair_programming:
    pair_programming_message = get_pair_programming_message()
    if len(slack_channel) > 0:
        send_slack_message_blocks(slack_token, slack_channel, [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":desktop_computer::bulb::computer:" + pair_programming_message
                }
            }
        ])

if Config.evaluate_pr_stats:
    # github stats
    if github_token and len(slack_token) > 0:
        # TODO github username should be added in developers.py
        # github-username: (name surname, is reviewer)
        developers = {"debiff": ["Simone Biffi", True],
                      "ncannata-dev": ["Nicola Cannata", False],
                      "Undermaken": ["Matteo Boschi", True],
                      "thisisjp": ["Jacopo Pompilii", True],
                      "pp - ps": ["Pietro Stroia", True],
                      "fabriziofff": ["Fabrizio Filizola", True],
                      "pietro909": ["Pietro Grandi", True],
                      "CrisTofani": ["Cristiano Tofani", True],
                      "andrea-favaro": ["Andrea Favarò", False]}
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=7)
        # it assumes that each item is a valid project inside pagopa org (https://github.com/pagopa)
        stats_for_projects = ['io-app']
        for project in stats_for_projects:
            pr_creaded = get_pull_requests_data(github_token, project, start, end)
            pr_reviews = get_pull_requests_data(github_token, project, start, end, 'closed', 'updated')
            stats = GithubStats(pr_creaded, pr_reviews)
            msg = f'*<https://github.com/pagopa/{project}|{project.upper()}>* repo stats (_experimental_)\n\n'
            msg += f':heavy_plus_sign: PR created `{stats.total_pr_created}`\n'
            msg += f':memo: PR reviewed `{stats.total_pr_reviewed}`\n'
            thread = send_slack_message_blocks(slack_token, pr_stats_slack_channel, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": msg
                    }
                }
            ])
            if stats.total_pr_reviewed == 0 and stats.total_pr_created == 0:
                continue
            # collect reviewers and sort by performance
            reviewers = list(reversed(sorted(filter(lambda k: developers.get(k, (k, False))[1], stats.data.keys()),
                                             key=lambda k: stats.data[k].contribution_ratio)))
            # collect not reviewers
            not_reviewers = list(filter(lambda k: k not in reviewers, stats.data.keys()))
            # put not reviewer at the end
            reviewers.extend(not_reviewers)
            for key in reviewers:
                value = stats.data[key]
                developer, is_reviewer = developers.get(key, (key, False))
                header = f'{developer}\n'
                msg = ''
                if is_reviewer:
                    msg += f'{get_reviewer_description(value)}\n'
                msg += f'PR created: {value.pr_created_count}\n'
                msg += f'PR created contribution: {value.pr_created_contribution}\n'
                msg += f'PR reviewed: {value.pr_review_count}\n'
                msg += f'PR reviewed contribution: {value.pr_review_contribution}\n'
                send_slack_message_blocks(slack_token, pr_stats_slack_channel, [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f'{header}```{msg}```'
                        }
                    }
                ], thread.data['ts'])
            send_slack_message_blocks(slack_token, pr_stats_slack_channel, [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":man-raising-hand::skin-tone-2::woman-raising-hand::skin-tone-2: Would you like to take part of this experiment with your repo?\n<https://github.com/pagopa/pivotal-stories/pulls|Submit a Pull Request>"
                    }
                }
            ], thread.data['ts'])
