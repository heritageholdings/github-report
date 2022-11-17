## Description
GitHub report is a simple tool that collects data from our repositories
and send them to a dedicated Slack channel as a weekly feed

## Setup
`Python` >= 3.5 is required<br/>
Make sure that all dependencies in [requirements.txt](requirements.txt) have been installed in your environment

`pip install -r requirements.txt`

### env variables
To work properly this tool needs some configuration in your environment variables

| key                   | description                                                                                                                                                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GH_TOKEN`             | required to use the GitHub API ([more info](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token))<br/>**note**: you can avoid to set it if your repo(s) are public |
| `GH_COMPANY_NAME` | the name of the company where repositories are (i.e. `heritageholdings`)                                                                                                                                                       |
| `GH_COMPANY_REPOSITORIES`  | a list of strings seperated by comma that contains the name of the repositories for which the reports will be produced (i.e. `iconic, repository2, repository3`)                                                               |
| `SLACK_TOKEN`         | *required* to send the report to a Slack dedicated channel ([more info](https://api.slack.com/apps))                                                                                                                           |
| `SLACK_CHANNEL`       | the name of the Slack channel where you want deliver the report messages (note: remember to install your app into that channel)                                                                                                |
| `DAYS_SPAN`           | the number of days from when this tool should collect the data (e.g if you want a report about the past week, set it to `7`)                                                                                                   |

### scheduled feed
The bot starts automatically collecting the data every Friday at 13.55 CET
[More info](/.github/workflows/scheduled_report.yml)