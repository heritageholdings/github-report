from dataclasses import dataclass
from typing import Any
import datetime
import requests
import os
from time import sleep

github_pr_url = 'https://api.github.com/search/issues?q=is:pr+repo:pagopa/'
github_review_url = 'https://api.github.com/repos/pagopa/io-app/pulls/%d/reviews'
github_token = os.getenv('GITHUB_TOKEN', "")
print(github_token)
headers = {'Authorization': f'Bearer {github_token}'}


def get_pull_requests_data(repo, from_date: datetime, to_date: datetime, state: str = None):
	base_url = github_pr_url + repo + (f'+state:{state}' if state else '')
	page = 1
	prs = []
	while True:
		url = base_url + f'+created:{from_date:%Y-%m-%d}..{to_date:%Y-%m-%d}&page={page}'
		print(f'page...{page}')
		req = requests.get(url, headers=headers)
		if req.status_code != 200:
			break
		data = req.json()
		if len(data["items"]) == 0:
			break
		for item in data["items"]:
			pr_url = item["pull_request"]["url"]
			req_url = github_review_url % item["number"]
			req_pr = requests.get(pr_url, headers=headers)
			sleep(0.2)
			req_review = requests.get(req_url, headers=headers)
			sleep(0.2)
			if req_pr.status_code != 200 or req_pr.status_code != 200:
				break
			prs.append(PullRequest(req_pr.json(),req_review.json()))
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


class GithubStats:

	def __init__(self, pull_requests):
		self.pull_requests = pull_requests
		self.data = {}
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


start = datetime.datetime(2020,9,1)
end = datetime.datetime(2021,12,10)
prs = get_pull_requests_data('io-app', start, end)
stats = GithubStats(prs)
for key,value in stats.data.items():
	print(key)
	print(f'created: {value.pr_created_count}')
	print(f'create contribution: {value.pr_created_contribution}')
	print(f'reviewed: {value.pr_review_count}')
	print(f'reviewed contribution: {value.pr_review_contribution}')
	print('-'*10)
