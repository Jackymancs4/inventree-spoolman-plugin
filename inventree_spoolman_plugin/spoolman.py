"""Sample implementation for ActionMixin."""

from plugin import InvenTreePlugin
from plugin.mixins import ActionMixin, APICallMixin, SettingsMixin, EventMixin


class SpoolmanPlugin(ActionMixin, APICallMixin, SettingsMixin, InvenTreePlugin):
    """An EXTREMELY simple action plugin which demonstrates the capability of the ActionMixin class."""

    NAME = 'SpoolmanPlugin'
    SLUG = 'spoolman'
    ACTION_NAME = 'spoolman'

    SETTINGS = {
        'API_URL': {
            'name': 'External URL',
            'description': 'Where is your API located?',
            'default': 'reqres.in',
        },
    }

    API_URL_SETTING = 'API_URL'

    result = {}

    @property
    def api_url(self):
        """Base url path."""
        return f'{self.get_setting(self.API_URL_SETTING)}'

    def perform_action(self, user=None, data=None):
        """Sample method."""
        print('Action plugin in action!')

        print(self.api_url)

        initial_response = self.api_call('api/v1/info', simple_response=False)

        if initial_response.status_code != 200:
            self.result = {'error'}
            return False
        
        filaments_response = self.api_call('api/v1/filament')

        self.result = filaments_response


    def get_info(self, user, data=None):
        """Sample method."""
        return {'user': user.username, 'hello': 'world'}

    def get_result(self, user=None, data=None):
        """Sample method."""
        return self.result
