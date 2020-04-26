import requests

SERVICES_URL = "https://www.pivotaltracker.com/services/v5"


class Pivotal:
    '''
    An utility class to get data from Pivotal APIs
    '''
    def __init__(self, api_token, api_url=SERVICES_URL):
        self._api_token = api_token
        self._auth_header = {'X-TrackerToken': self._api_token}
        self._api_url = api_url

    def get_project(self, project_id):
        return self._execute_get('/projects/%d' % project_id)

    def get_project_membership(self, project_id):
        '''
        return all members involved in pivotal project
        :param project_id: pivotal project id
        :return:
        '''
        return self._execute_get('/projects/%d/memberships' % project_id)

    def get_stories(self, project_id, updated_since, story_state=["accepted"]):
        '''
        :param project_id: the id of the pivotal project
        :param updated_since: a date with format mm/dd/yyyy
        :param story_state: a list of story states used as filter
        :return: a list of stories
        '''
        stories = []
        offset = 0

        while True:
            stories_slice = self._execute_get(
                '/projects/%d/stories?filter=updated_since:%s AND state:%s&offset=%d' % (
                    project_id, updated_since, ",".join(story_state), offset))
            if len(stories_slice) == 0:
                break
            stories.extend(stories_slice)
            offset = len(stories)
        return stories

    @property
    def me(self):
        return self.get_me()

    def get_me(self):
        """
        retrieve me user data
        to know how it looks like: http://jsoneditoronline.org/?id=3fe7ee8d4c34456a8f4232f3e33e2376
        :return a dictionary with data
        """
        return self._execute_get("/me")

    def _execute_get(self, path):
        path = "/" + path if not path.startswith("/") else path
        path = '%s%s' % (self._api_url, path)
        req = requests.get(path, headers=self._auth_header)
        if req.status_code == 200:
            return req.json()
        raise Exception("cant load data from %s [%d]" % (path, req.status_code))
