## Description
Github report is a simple tool that collects data from our repositories
and send them to a dedicated Slack channel as feed

## Setup
Make sure that all dependencies in [requirements.txt](requirements.txt) have been installed in your environment
`pip install -r requirements.txt`

### env variables
To works properly this tool needs some configuration data

| key | description                                                                                                                                                   |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
|`GITHUB_TOKEN` | required to use the GitHub API ([more info](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)) |
| `GITHUB_COMPANY_NAME` | the name of the company where repositories are (i.e `heritageholdings`)                                                                                                         |
|`SLACK_TOKEN` | required to send the report to a Slack dedicated channel ([more info](https://api.slack.com/apps))                                                            |
| `SLACK_CHANNEL` | the name of the Slack channel where the app that holds the previos token is installed                                                                         |

