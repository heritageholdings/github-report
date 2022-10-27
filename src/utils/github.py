from dataclasses import dataclass
from typing import Literal, List, Dict
from datetime import datetime
from github import Github
from github.PullRequest import PullRequest as GithubPullRequest

from utils.env import GITHUB_TOKEN, GITHUB_COMPANY_NAME

PRStatus = Literal["open", "closed", "draft", "merged"]


@dataclass(frozen=True)
class GithubUser:
    login_name: str
    name: str


class PullRequestByStatus:

    def __init__(self):
        self.merged: List[PullRequest] = []
        self.open: List[PullRequest] = []
        self.closed: List[PullRequest] = []
        self.reviewed: List[PullRequest] = []
        self.draft: List[PullRequest] = []


class PullRequest:
    """
    This class holds the minimal set of a PR data used to do stats
    """

    def __init__(self, pr: GithubPullRequest):
        self.state: PRStatus
        if pr.merged:
            self.state = "merged"
        elif pr.draft:
            self.state = "draft"
        else:
            self.state = pr.state
        self.number: int = pr.number
        self.title: str = pr.title
        self.author: GithubUser = GithubUser(pr.user.login, pr.user.name)
        self.merged: bool = pr.merged
        self.draft: bool = pr.draft
        self.merged_by: GithubUser = GithubUser(pr.merged_by.login, pr.merged_by.name) if pr.merged else None
        self.additions: int = pr.additions
        self.deletions: int = pr.deletions
        self.created_at: datetime = pr.created_at
        self.url: str = pr.html_url
        self.contribution = self.additions + self.deletions
        self.reviewers = set(map(lambda r: GithubUser(r.user.login, r.user.name),
                                 filter(lambda r: r.state in ("APPROVED", "CHANGES_REQUESTED"), pr.get_reviews())))


def get_pull_requests_recently_updated(repository_name: str, days_before: int) -> List[
    PullRequest]:
    """
    return the list of the pull requests updated between days_before ago and now
    :param repository_name:
    :param days_before:
    :return:
    """
    now = datetime.now()
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{GITHUB_COMPANY_NAME}/{repository_name}")
    data = repo.get_pulls(state="all", sort="updated", direction="desc")
    pull_requests = []
    for pull in data:
        # the PR is older than we are looking for, break since the following ones are older
        if (now - pull.updated_at).days > days_before:
            break
        pull_requests.append(PullRequest(pull))
    return pull_requests


def get_pull_requests_recently_created(repository_name: str, days_before: int) -> List[
    PullRequest]:
    """
    return the list of the pull requests created between days_before ago and now
    :param repository_name:
    :param days_before:
    :return:
    """
    now = datetime.now()
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{GITHUB_COMPANY_NAME}/{repository_name}")
    data = repo.get_pulls(state="all", sort="created", direction="desc")
    pull_requests = []
    for pull in data:
        # the PR is older than we are looking for, break since the following ones are older
        if (now - pull.created_at).days > days_before:
            break
        pull_requests.append(PullRequest(pull))
    return pull_requests


def get_pull_requests(repository_name: str) -> List[
    PullRequest]:
    """
    return the list of the current pull requests (open, draft)
    :param repository_name:
    :return:
    """
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{GITHUB_COMPANY_NAME}/{repository_name}")
    data = repo.get_pulls(state="open", sort="created", direction="desc")
    pull_requests = []
    for pull in data:
        pull_requests.append(PullRequest(pull))
    return pull_requests


def group_by_state(pull_requests: List[PullRequest]) -> PullRequestByStatus:
    """
    note PR can be simultaneously in merged and reviewed state (it means it has been merged and someone approved it)
    :param pull_requests:
    :return:
    """
    by_state = PullRequestByStatus()
    for pr in pull_requests:
        if pr.state == "merged":
            if len(pr.reviewers):
                by_state.reviewed.append(pr)
        getattr(by_state, pr.state).append(pr)
    return by_state


@dataclass
class DeveloperContribution:
    developer: GithubUser
    contribution: int
    review_contribution: int
    pr_reviewed: List[str]
    pr_created: List[str]


def group_by_developer(pull_requests: List[PullRequest]) -> Dict:
    """
    from the given pull_requests list, return a dictionary where the key is the login name of the developer
    and the value is his/her contribution (DeveloperContribution)
    a developer can contribute on PR by creating or by reviewing it
    :param pull_requests:
    :return:
    """
    by_developer = {}
    for pr in pull_requests:
        developer_contribution = by_developer.get(pr.author.login_name, DeveloperContribution(pr.author, 0, 0, [], []))
        developer_contribution.contribution += pr.contribution
        developer_contribution.pr_created.append(pr.number)
        by_developer[developer_contribution.developer.login_name] = developer_contribution
        for review in pr.reviewers:
            review_developer_contribution = by_developer.get(review.login_name,
                                                             DeveloperContribution(review, 0, 0, [], []))
            review_developer_contribution.review_contribution += pr.contribution
            review_developer_contribution.pr_reviewed.append(pr.number)
            by_developer[review_developer_contribution.developer.login_name] = review_developer_contribution
    return by_developer
