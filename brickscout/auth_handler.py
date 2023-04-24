from . import config
from urllib.parse import urlencode
import json

class AuthHandler:

    def __init__(self, api: 'BrickScoutAPI') -> None:
        self._api = api
        self._cache_handler = api._cache_handler
        
        self._auth_url = config.AUTH_URL
        self._username = api._username
        self._password = api._password
        
        self._client_id = self._client_secret = 'brickscout'
        self._grant_type = 'password'
        
        if not self._username or not self._password:
            raise ValueError('Username and password are required to authenticate.')
        
    def get_tokens(self) -> str:
        """ Returns the tokens for the user. Checks the cache first. If not found, authenticates and returns the tokens. """
        
        # Check if the token is in the cache
        cached_tokens = self._cache_handler.get(self._username)
        if cached_tokens:
            return cached_tokens
        
        # If not, authenticate and return the token
        tokens = self._authenticate()
        return tokens
        
    def _authenticate(self) -> dict:
        """ Authenticates the user and returns the tokens. """
        
        params = {
            'client_id' : self._client_id,
            'client_secret' : self._client_secret,
            'grant_type' : self._grant_type,
            'username' : self._username,
            'password' : self._password
        }
        
        auth_url = f'{self._auth_url}/token?{urlencode(params)}'
        
        # Make the request
        response = self._api._do_request('POST', auth_url, prepend_base_to_url=False)
        response_type = response.headers.get('Content-Type')
        status_code = response.status_code
        content = response.json() if 'application/json' in response_type else response.text
        
        # Check if the request was successful
        if status_code != 200:
            raise Exception(f'Error while authenticating: {content}')
        
        # Write the tokens to the cache
        self._cache_handler.write(self._username, content)
        
        return content

        