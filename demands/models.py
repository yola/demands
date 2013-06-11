import logging

from urlparse import urljoin
from requests import Session


log = logging.getLogger(__name__)


class HTTPServiceError(Exception):
    def __init__(self, code, details):
        self.code = code
        self.details = details
        super(Exception, self).__init__(
            'code: %s, details: %s' % (code, details)
        )


class HTTPService(Session):
    """Extendable base service client object"""

    def __init__(self, url, **kwargs):
        super(HTTPService, self).__init__()
        self.url = url
        self.request_params = {}
        self.expected_response_codes = []
        self.update(**kwargs)

    def update(self, **kwargs):
        """Extract custom parameters, update request parameters"""
        if 'expected_response_codes' in kwargs:
            self.expected_response_codes = kwargs.pop(
                'expected_response_codes')

        if 'username' in kwargs:
            self.request_params['auth'] = (
                kwargs.pop('username'),
                kwargs.pop('password', None)
            )

        if 'client_name' in kwargs:
            headers = self.request_params.get('headers') or {}
            headers.update(kwargs.pop('headers', {}))
            headers.update({
                'User-Agent': '%s %s - %s' % (
                    kwargs.pop('client_name'),
                    kwargs.pop('client_version', 'x.y.z'),
                    kwargs.pop('app_name', 'unknown'),
                )
            })
            self.request_params['headers'] = headers

        self.request_params.update(kwargs)

    def request(self, method, path, **kwargs):
        self.update(**kwargs)
        url = urljoin(self.url, path)
        response = super(HTTPService, self).request(
            method, url, **self.request_params)
        self.post_send(response)
        return response

    def post_send(self, response):
        """Ensure successful responses from API endpoints"""
        response.is_ok = response.status_code < 300
        expected_code = response.status_code in self.expected_response_codes
        if not (response.is_ok or expected_code):
            log.error(
                'Unexpected response from %s: url: %s, code: %s, details: %s',
                self.__class__.__name__, response.url, response.status_code,
                response.content)
            raise HTTPServiceError(response.status_code, response.content)
