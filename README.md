## Description
Github report is a simple tool that collects data from our repositories
and send them to a dedicated Slack channel as feed

## Setup
Make sure that all dependencies in [requirements.txt](requirements.txt) have been installed in your environment
`pip install -r requirements.txt`

### env variables
To work properly this tool needs some configuration data

| key                   | description                                                                                                                                                   |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GH_TOKEN`             | required to use the GitHub API ([more info](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)) |
| `GH_COMPANY_NAME` | the name of the company where repositories are (i.e. `heritageholdings`)                                                                                      |
|  `GH_COMPANY_REPOSITORIES`  | an array of strings that contains the name of the repositories for which the report will be produced (i.e. `['iconic']`)                            |
| `SLACK_TOKEN`         | required to send the report to a Slack dedicated channel ([more info](https://api.slack.com/apps))                                                            |
| `SLACK_CHANNEL`       | the name of the Slack channel where the app that holds the previos token is installed                                                                         |
| `DAYS_SPAN`           | the number of days from when tool should collect the data (e.g if you want a report about the last week, set it to `7`)                                       |

### scheduled feed
The bot starts automatically collecting the data every Friday at 13.55 CET
[More info](/.github/workflows/scheduled_report.yml)