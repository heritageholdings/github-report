from dataclasses import dataclass
from typing import Any
import datetime
import requests
from time import sleep
import math

github_pr_url = 'https://api.github.com/search/issues?q=is:pr+repo:pagopa/'
github_review_url = 'https://api.github.com/repos/pagopa/io-app/pulls/%d/reviews'


@dataclass
class PullRequest:
	pr_data: Any
	pr_review_data: Any

	@property
	def author(self):
		return self.pr_data["user"]["login"]

	@property
	def additions(self):
		return self.pr_data["additions"]

	@property
	def deletions(self):
		return self.pr_data["deletions"]

	@property
	def contribution(self):
		return self.additions + self.deletions

	@property
	def reviewers(self):
		'''
		collect all reviewers name that contribute to PR approving
		note: it's used a list instead of a set to allow duplicates
		:return:
		'''
		reviewers = []
		if self.pr_review_data:
			for d in self.pr_review_data:
				if d["state"] == "APPROVED":
					reviewers.append(d["user"]["login"])
		return reviewers


class Stats:
	def __init__(self):
		self.pr_created_count = 0
		self.pr_created_contribution = 0
		self.pr_review_count = 0
		self.pr_review_contribution = 0

	@property
	def contribution_ratio(self):
		if self.pr_created_contribution == 0:
			return 0
		return self.pr_review_contribution / self.pr_created_contribution


class GithubStats:

	def __init__(self, pull_requests):
		self.pull_requests = pull_requests
		self.data = {}
		self.total_pr_created = 0
		self.total_pr_reviewed = 0
		self.compute()

	def compute(self):
		'''
		indexing author stats by author name (github name)
		:return:
		'''
		pr_created = 0
		pr_reviewed = 0
		for pr in self.pull_requests:
			if pr.author not in self.data:
				self.data[pr.author] = Stats()
			self.data[pr.author].pr_created_contribution += pr.contribution
			self.data[pr.author].pr_created_count += 1
			pr_created += 1
			pr_reviewed += 1 if len(pr.reviewers) > 0 else 0
			for reviewer in pr.reviewers:
				if reviewer not in self.data:
					self.data[reviewer] = Stats()
				self.data[reviewer].pr_review_count += 1
				self.data[reviewer].pr_review_contribution += pr.contribution
		all_prs = self.data.values()
		# compute all PR created and reviewed
		self.total_pr_created = pr_created
		self.total_pr_reviewed = pr_reviewed


def get_pull_requests_data(github_token, repo, from_date: datetime, to_date: datetime, state: str = None):
	headers = {'Authorization': f'Bearer {github_token}'}
	base_url = github_pr_url + repo + (f'+state:{state}' if state else '')
	page = 1
	prs = []
	while True:
		# request pr created in a date span
		url = base_url + f'+created:{from_date:%Y-%m-%d}..{to_date:%Y-%m-%d}&page={page}'
		print(url)
		req = requests.get(url, headers=headers)
		if req.status_code != 200:
			break
		data = req.json()
		# no more items
		if len(data["items"]) == 0:
			break
		for item in data["items"]:
			pr_url = item["pull_request"]["url"]
			# get pr details
			req_pr = requests.get(pr_url, headers=headers)
			sleep(0.1)
			# get pr reviewers details
			req_url = github_review_url % item["number"]
			req_review = requests.get(req_url, headers=headers)
			if req_pr.status_code != 200 or req_pr.status_code != 200:
				continue
			prs.append(PullRequest(req_pr.json(), req_review.json()))
		page += 1
	return prs


def get_reviewer_description(stats: Stats):
	if stats.pr_created_contribution == 0 and stats.pr_review_contribution > 0:
		return '🎖️ reviewer'
	contribution_ratio = 0 if stats.contribution_ratio <= 0.1 else stats.contribution_ratio
	msg = f'{stats.contribution_ratio: .2f} (reviewed / created)'
	if contribution_ratio == 0:
		return f'🤨 {msg}'
	if contribution_ratio >= 1:
		return f'🏆 {msg}'
	return '⭐' * math.ceil(contribution_ratio / 0.2) + f' {msg}'

