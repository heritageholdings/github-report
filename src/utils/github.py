import requests

github_pr_url = 'https://api.github.com/search/issues?q=is:pr+repo:pagopa/io-app'
github_review_url = 'https://api.github.com/repos/pagopa/io-app/pulls/%d/reviews'
token = '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'
headers = {'Authorization' : f'Bearer {token}'}
def get_pull_requests(from_date,to_date, state = None):
	base_url = github_pr_url + (f'+state:{state}' if state else '')
	page = 1
	prs = []
	while True:
		url = base_url + f'+created:{from_date:%Y-%m-%d}..{to_date:%Y-%m-%d}&page={page}'
		print(f'page...{page}')
		req = requests.get(url, headers = headers)
		if req.status_code == 200:
			data = req.json()
			if len(data["items"]) == 0:
				break
			prs.extend(data["items"])
		else:
			print(req.status_code)
		page += 1
	return prs

def get_pull_requests_reviewer(pr_id):
	url = github_review_url % pr_id
	print(f'request pr {pr_id}')
	req = requests.get(url, headers = headers)
	reviewers = []
	if req.status_code == 200:
		data = req.json()
		for d in data:
			if d["state"] == "APPROVED":
				reviewers.append(d["user"]["login"])
	else:
		print(req.status_code)
	return reviewers

import datetime
now = datetime.datetime.now()
week_ago = now - datetime.timedelta(days=60)
all_prs = get_pull_requests(week_ago,now,None)
devs = {'Undermaken' : {'name': 'Matteo Boschi', 'author' : 0, 'reviewer' : 0 },
		'CrisTofani' : {'name': 'Cristiano Tofani', 'author' : 0, 'reviewer' : 0 },
		'fabriziofff' : {'name': 'Fabrizio Filizola', 'author' : 0, 'reviewer' : 0 },
		'debiff' : {'name': 'Simone Biffi', 'author' : 0, 'reviewer' : 0 }}
for pr in all_prs:
	if pr["user"]["login"] in devs:
		devs[pr["user"]["login"]]["author"] += 1
	reviewers = get_pull_requests_reviewer(pr["number"])
	from time import sleep
	sleep(0.5)
	for r in reviewers:
		if r in devs:
			devs[r]["reviewer"] += 1

for dev in devs.values():
	print(f'{dev["name"],dev["author"],dev["reviewer"]}')
