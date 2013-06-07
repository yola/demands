import logging
import requests
import time


log = logging.getLogger(__name__)


class Request(object):
    """Request object for http requests/responses."""

    def __init__(self, url, method, cookies=None, data=None, headers=None,
                 params=None, verify=True):
        self.url = url
        self.method = method
        self.cookies = cookies or {}
        self.data = data or {}
        self.headers = headers or {}
        self.params = params or {}
        self.verify = verify
        self.auth = None

    def _compose_request_arguments(self):
        """Compose arguments as expected by the requests library."""
        arguments = {}
        arguments['params'] = self.params
        arguments['data'] = self.data
        arguments['cookies'] = self.cookies
        arguments['headers'] = self.headers
        arguments['auth'] = self.auth
        arguments['verify'] = self.verify
        return arguments

    def authenticate(self, username, password):
        """Enable http username/pass authentication. """
        log.debug('Authentication via HTTP auth as "%s"', username)
        self.auth = (username, password)

    def send(self):
        """Execute the request and return the response."""
        method = self.method.lower()
        request_arguments = self._compose_request_arguments()
        start_time = time.time()
        response = getattr(requests, method)(self.url, **request_arguments)
        log.debug('%s HTTP [%s] call to "%s" %.2fms',
                  response.status_code, self.method, self.url,
                  (time.time() - start_time) * 1000)
        log.debug('HTTP request args: %s', request_arguments)
        return response


class HTTPServiceError(Exception):
    def __init__(self, code, details):
        self.code = code
        self.details = details
        super(Exception, self).__init__(
            'code: %s, details: %s' % (code, details)
        )


class HTTPService(object):
    """Extendable base service client object"""

    def __init__(self, url=None, verify=True, username=None, password=None,
                 client_name=None, client_version='x.y.z', app_name='unknown'):

        assert url, "HTTPService requires 'url'"

        self.url = url
        self.verify = verify
        self.username = username
        self.password = password
        self.client_name = client_name
        self.client_version = client_version
        self.app_name = app_name
        
    def pre_send(self, request, **kwargs):
        """Called just before sending request.

        Used to modify the request object before the request is sent.

        """
        if self.username:
            request.authenticate(self.username, self.password)

        if self.client_name:
            request.headers['User-Agent'] = '%s %s - %s' % (
                self.client_name,
                self.client_version,
                self.app_name,
            )

    def post_send(self, request, response, **kwargs):
        """Called after request is sent.

        Override to modify response object returned by call made by
        request object.

        """
        response.is_ok = response.status_code < 300
        expected_codes = kwargs.get('expected_response_codes', [])
        if not (response.is_ok or response.status_code in expected_codes):
            log.error(
                'Unexpected response from %s: url: %s, code: %s, details: %s',
                self.__class__.__name__, response.url, response.status_code,
                response.content)
            raise HTTPServiceError(response.status_code, response.content)

    def get(self, path, **kwargs):
        return self._make_call('GET', path, **kwargs)

    def post(self, path, **kwargs):
        return self._make_call('POST', path, **kwargs)

    def put(self, path, **kwargs):
        return self._make_call('PUT', path, **kwargs)

    def patch(self, path, **kwargs):
        return self._make_call('PATCH', path, **kwargs)

    def delete(self, path, **kwargs):
        return self._make_call('DELETE', path, **kwargs)

    def _make_call(self, method, path, **kwargs):
        """Call the service method defined by the passed path and http method.

        Additional arguments include cookies, headers, body, and data values.

        """
        base = self.url
        url = '/'.join([base.rstrip('/'), path.lstrip('/')])

        request = Request(url, method, **kwargs)

        self.pre_send(request, **kwargs)
        response = request.send()
        self.post_send(request, response, **kwargs)
        return response
