import logging
import requests
import time


log = logging.getLogger(__name__)


class Request(object):
    """Request object which provides functionality to send and receive
    http requests/responses.
    """

    def __init__(self, url, method, data, headers, cookies, verify):
        self.url = url
        self.method = method

        self.requests_args = {}

        if method in ('POST', 'PUT', 'PATCH'):
            self.requests_args['data'] = data
        else:
            self.requests_args['params'] = data

        self.requests_args['cookies'] = cookies
        self.requests_args['headers'] = headers

        if self.url.startswith('https'):
            self.requests_args['verify'] = verify

    def authenticate(self, username, password):
        """Enable http authentication with the provided username and
        password
        """
        log.debug('Authentication via HTTP auth as "%s"', username)
        self.requests_args['auth'] = (username, password)

    def send(self):
        """Execute the request, and return the response"""
        method = self.method.lower()
        start_time = time.time()
        response = getattr(requests, method)(self.url, **self.requests_args)
        log.debug('%s HTTP [%s] call to "%s" %.2fms', response.status_code, self.method, self.url,
                  (time.time() - start_time) * 1000)
        log.debug('HTTP request data: %s', self.requests_args)
        return response


class HTTPServiceError(Exception):
    def __init__(self, code, details):
        self.code = code
        super(Exception, self).__init__(
            'code: %s, details: %s' % (code, details)
        )


class HTTPService(object):
    """Provides an interface which allows arbitrary methods to be defined and
    called on a remote http service.
    """
    def __init__(self, config):
        self.config = config

    def pre_send(self, request, **params):
        """Override to modify request object to be called just before sending
        the request"""
        if self.config.get('username'):
            request.authenticate(
                self.config['username'], self.config['password'])

    def post_send(self, request, response, **params):
        """Override to modify response object returned by call made by request
        object.
        """
        response.is_ok = response.status_code < 300
        if (not response.is_ok and
                not response.status_code in params.get('expected_response_codes', [])):
            log.error('Unexpected response from %s: url: %s, code: %s, details: %s',
                self.__class__.__name__, response.url, response.status_code, response.content)

            raise HTTPServiceError(response.status_code, response.content)

    def get(self, path, data=None, cookies=None, headers=None, **kwargs):
        return self._make_call('GET', path, data, cookies, headers, **kwargs)

    def post(self, path, data=None, cookies=None, headers=None, **kwargs):
        return self._make_call('POST', path, data, cookies, headers, **kwargs)

    def put(self, path, data=None, cookies=None, headers=None, **kwargs):
        return self._make_call('PUT', path, data, cookies, headers, **kwargs)

    def delete(self, path, data=None, cookies=None, headers=None, **kwargs):
        return self._make_call('DELETE', path, data, cookies, headers, **kwargs)

    def _make_call(self, method, path, data, headers, cookies, **kwargs):
        """Call the service method defined by the passed path and http method.
        Additional arguments include cookies, headers, and data values.
        """
        base = self.config.get('url')
        url = '/'.join([base.rstrip('/'), path.lstrip('/')])

        request = Request(url, method, data, headers, cookies, self.config.get('verify_ssl', True))

        self.pre_send(request, **kwargs)
        response = request.send()
        self.post_send(request, response, **kwargs)
        return response
