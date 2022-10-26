from dataclasses import dataclass
from typing import Literal, List, Union, TypedDict
from datetime import datetime
from github import Github
from github.PullRequest import PullRequest as GithubPullRequest

from utils.env import GITHUB_TOKEN, GITHUB_COMPANY_NAME

PRStatus = Literal["open", "closed", "draft"]


@dataclass(frozen=True)
class GithubUser:
    login_name: str
    name: str


class PullRequest:
    """
    This class holds the minimal set of a PR data used to do stats
    """

    def __init__(self, pr: GithubPullRequest):
        self.state: PRStatus = pr.state
        self.number: int = pr.number
        self.title: str = pr.title
        self.author: GithubUser = GithubUser(pr.user.login, pr.user.name)
        self.merged: bool = pr.merged
        self.merged_by: GithubUser = GithubUser(pr.merged_by.login, pr.merged_by.name) if pr.merged else None
        self.additions: int = pr.additions
        self.deletions: int = pr.deletions
        self.created_at: datetime = pr.created_at
        self.url: str = pr.html_url
        self.contribution = self.additions + self.deletions
        self.reviewers = set(map(lambda r: GithubUser(r.user.login, r.user.name),
                                 filter(lambda r: r.state in ("APPROVED", "CHANGES_REQUESTED"), pr.get_reviews())))


def get_repo_stats2(repository_name: str, days_before: int, state: Union[PRStatus, Literal["all"]] = "all") -> List[
    PullRequest]:
    now = datetime.now()
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{GITHUB_COMPANY_NAME}/{repository_name}")
    data = repo.get_pulls(state=state, sort="created", direction="desc")
    pull_requests = []
    for pull in data:
        # the PR is older than we are looking for, break since the following ones are older
        if (now - pull.updated_at).days > days_before:
            break
        pull_requests.append(PullRequest(pull))
    return pull_requests


class PRStatusCounter(TypedDict):
    merged: List[PullRequest]
    open: List[PullRequest]
    closed: List[PullRequest]
    reviewed: List[PullRequest]
    draft: List[PullRequest]


def group_by_state(pull_requests: List[PullRequest]) -> PRStatusCounter:
    """
    return a dictionary where the key is the PR state e the value the amount of the PR in that state
    states can be: open, closed, draft, merged, reviewed
    a PR can be simultaneously in merged and reviewed state (it means it has been merged and someone approved it)
    :param pull_requests:
    :return:
    """
    by_state = {}
    for pr in pull_requests:
        if pr.merged:
            by_state["merged"] = by_state.get("merged", [])
            by_state["merged"].append(pr)
            if len(pr.reviewers):
                by_state["reviewed"] = by_state.get("reviewed", [])
                by_state["reviewed"].append(pr)
            continue
        by_state[pr.state] = by_state.get(pr.state, [])
        by_state[pr.state].append(pr)
    return by_state


@dataclass
class DeveloperContribution:
    developer: GithubUser
    contribution: int
    review_contribution: int
    pr_reviewed: List[str]
    pr_created: List[str]



def group_by_developer(pull_requests: List[PullRequest]):
    by_developer = {}
    for pr in pull_requests:
        developer_contribution = by_developer.get(pr.author.login_name, DeveloperContribution(pr.author, 0, 0, [], []))
        developer_contribution.contribution += pr.contribution
        developer_contribution.pr_created.append(pr.number)
        by_developer[developer_contribution.developer.login_name] = developer_contribution
        for review in pr.reviewers:
            review_developer_contribution = by_developer.get(review.login_name, DeveloperContribution(review, 0, 0, [], []))
            review_developer_contribution.review_contribution += pr.contribution
            review_developer_contribution.pr_reviewed.append(pr.number)
            by_developer[review_developer_contribution.developer.login_name] = review_developer_contribution
    return by_developer
