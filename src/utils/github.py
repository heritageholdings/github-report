import requests

github_pr_url = 'https://api.github.com/search/issues?q=is:pr+repo:pagopa/io-app'

def get_pull_requests(from_date,to_date, state = None):
	url = github_pr_url + (f'+state:{state}' if state else '')
	url += f'+created:{from_date:%Y-%m-%d}..{to_date:%Y-%m-%d}'
	req = requests.get(url)
	if req.status_code == 200:
		data = req.json()
		return data["items"]
	return []

import datetime
now = datetime.datetime.now()
week_ago = now - datetime.timedelta(days=7)
get_pull_requests(week_ago,now,None)

