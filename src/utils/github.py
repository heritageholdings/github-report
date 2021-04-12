from dataclasses import dataclass
from typing import Any
import datetime
import requests
import os
from time import sleep

github_pr_url = 'https://api.github.com/search/issues?q=is:pr+repo:pagopa/'
github_review_url = 'https://api.github.com/repos/pagopa/io-app/pulls/%d/reviews'


def get_pull_requests_data(github_token, repo, from_date: datetime, to_date: datetime, state: str = None):
	headers = {'Authorization': f'Bearer {github_token}'}
	base_url = github_pr_url + repo + (f'+state:{state}' if state else '')
	page = 1
	prs = []
	while True:
		url = base_url + f'+created:{from_date:%Y-%m-%d}..{to_date:%Y-%m-%d}&page={page}'
		req = requests.get(url, headers=headers)
		if req.status_code != 200:
			break
		data = req.json()
		if len(data["items"]) == 0:
			break
		exit = False
		for item in data["items"]:
			created_at = datetime.datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%SZ')
			if created_at > to_date:
				exit = True
				break
			pr_url = item["pull_request"]["url"]
			req_url = github_review_url % item["number"]
			req_pr = requests.get(pr_url, headers=headers)
			sleep(0.1)
			req_review = requests.get(req_url, headers=headers)
			if req_pr.status_code != 200 or req_pr.status_code != 200:
				exit = True
				break
			prs.append(PullRequest(req_pr.json(), req_review.json()))
		if exit:
			break
		page += 1
	return prs


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
		for pr in self.pull_requests:
			if pr.author not in self.data:
				self.data[pr.author] = Stats()
			self.data[pr.author].pr_created_contribution += pr.contribution
			self.data[pr.author].pr_created_count += 1
			for reviewer in pr.reviewers:
				if reviewer not in self.data:
					self.data[reviewer] = Stats()
				self.data[reviewer].pr_review_count += 1
				self.data[reviewer].pr_review_contribution += pr.contribution
		all_prs = self.data.values()
		self.total_pr_created = sum(map(lambda item: item.pr_created_count, all_prs))
		self.total_pr_reviewed = sum(map(lambda item: item.pr_review_count, all_prs))


def get_reviewer_emoji(contribution):
	import math
	if contribution == 0:
		return '🤨'
	if contribution >= 1:
		return '🔝'
	return '⭐' * math.ceil(contribution / 0.2)