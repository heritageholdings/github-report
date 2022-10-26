from dataclasses import dataclass
from typing import Literal, List
from datetime import datetime
from github import Github
from github.PullRequest import PullRequest as GithubPullRequest

from utils.env import GITHUB_TOKEN, GITHUB_COMPANY_NAME

PRStatus = Literal["open", "closed", "all"]

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
        self.title: str = pr.title
        self.author_login: GithubUser = GithubUser(pr.user.login, pr.user.name)
        self.merged: bool = pr.merged
        self.merged_by: GithubUser = GithubUser(pr.merged_by.login, pr.merged_by.name) if pr.merged else None
        self.additions: int = pr.additions
        self.deletions: int = pr.deletions
        self.created_at: datetime = pr.created_at
        self.url: str = pr.html_url
        self.reviewers = set(map(lambda r: GithubUser(r.user.login, r.user.name),
                                 filter(lambda r: r.state in ("APPROVED", "CHANGES_REQUESTED"), pr.get_reviews())))


def get_repo_stats2(repository_name: str, days_before: int, state: PRStatus = "all") -> List[PullRequest]:
    now = datetime.now()
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{GITHUB_COMPANY_NAME}/{repository_name}")
    data = repo.get_pulls(state=state, sort="created", direction="desc")
    pull_requests = []
    for pull in data:
        # the PR is older than we are looking for
        if (now - pull.updated_at).days > days_before:
            break
        pull_requests.append(PullRequest(pull))
    return pull_requests


def group_by_state(pull_requests: List[PullRequest]):
    by_state = {"created": len(pull_requests)}
    for pr in pull_requests:
        if pr.merged:
            by_state["merged"] = by_state.get("merged", 0) + 1
            if len(pr.reviewers):
                by_state["reviewed"] = by_state.get("reviewed", 0) + 1
        elif pr.state == "open":
            by_state["open"] = by_state.get("open", 0) + 1
        elif pr.state == "draft":
            by_state["draft"] = by_state.get("draft", 0) + 1
        elif pr.state == "closed":
            print(pr.url)
            by_state["closed"] = by_state.get("closed", 0) + 1
    return by_state
