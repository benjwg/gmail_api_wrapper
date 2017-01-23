import logging
import os
import ujson

import tornado.gen
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat
from tornadoalf.client import Client, TokenManager

import settings

API_URL = 'https://www.googleapis.com/gmail/v1'
OAUTH_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'


class AuthTokenManager(TokenManager):
    @tornado.gen.coroutine
    def _request_token(self):
        auth_details = {
            'grant_type': 'refresh_token',
            'scope': OAUTH_SCOPE,
            'refresh_token': settings.OAUTH_REFRESH_TOKEN,
            'client_id': settings.OAUTH_CLIENT_ID,
            'client_secret': settings.OAUTH_CLIENT_SECRET
        }

        token_data = yield self._fetch(
            url=OAUTH_TOKEN_ENDPOINT,
            method='POST',
            auth=None,
            data=auth_details
        )
        raise tornado.gen.Return(token_data)


class OAuthClient(Client):
    token_manager_class = AuthTokenManager


class GmailAPI(object):
    def prepare_request(self, parameters):
        url = os.path.join(API_URL, 'users', settings.GMAIL_USER_ID)

        for r in ['resource', 'subresource']:
            if parameters.get(r) is not None:
                url = os.path.join(url, parameters.pop(r))
                if parameters.get(r + '_id') is not None:
                    url = os.path.join(url, parameters.pop(r + 'id'))

        return HTTPRequest(url_concat(url, parameters))

    def request(self, parameters=None, callback=None):
        def intermediate_callback(resp):
            return callback(self.handle_response(resp))

        request = self.prepare_request(parameters=parameters)

        client = OAuthClient(
            token_endpoint=OAUTH_TOKEN_ENDPOINT,
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET)

        client.fetch(request, callback=intermediate_callback)

    def handle_response(self, response):
        if not 200 <= response.code < 300:
            logging.error('API error: HTTP %r: %r; %r',
                          response.code, response.body, response.effective_url)
            return None, HTTPError(response.code, response.reason, response)
        return ujson.loads(response.body), None
