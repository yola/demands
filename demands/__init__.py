import copy
import inspect
import logging
import time

from requests import Session
from six import PY2, iteritems, itervalues

__doc__ = 'Base HTTP service client'
__version__ = '5.1.0'
__url__ = 'https://github.com/yola/demands'

log = logging.getLogger(__name__)


def get_args(fun):
    if PY2:
        return inspect.getargspec(fun)[0]
    return tuple(p.name for p in inspect.signature(fun).parameters.values())


class HTTPServiceError(AssertionError):
    def __init__(self, response):
        """
        :param response: the HTTP response which was deemed in error
        """
        self.response = response
        try:
            self.details = response.json()
        except ValueError:
            self.details = response.content
        super(AssertionError, self).__init__(
            'Unexpected response: url: %s, code: %s, details: %s' % (
                response.url, response.status_code, self.details)
        )


class HTTPServiceClient(Session):
    """Extendable base service client.

    Client can be configured with any param allowed by the requests API. These
    params will be uses with each and every request and can be overridden with
    kwargs.  `demands` adds the following params:

    :param expected_response_codes: (optional) Workaround for services which
        returns non-expected results, example: when search for users, and
        expect [] for when nobody is found, yet a 404 is returned.
    :param client_name: (optional) Sets the User-Agent header.  Important
        because we want to accurately log errors and throw deprecation
        warnings when clients are outdated
    :param client_version: (optional) Used with client_name
    :param app_name: (optional) Used with client_name
    :param cookies: (optional) Dict only, CookieJar not supported
    """

    _VALID_REQUEST_ARGS = get_args(Session.request)

    def __init__(self, url, **kwargs):
        super(HTTPServiceClient, self).__init__()
        self.url = url

        if 'client_name' in kwargs:
            kwargs.setdefault('headers', {})
            kwargs['headers']['User-Agent'] = '%s %s - %s' % (
                kwargs.get('client_name'),
                kwargs.get('client_version', 'x.y.z'),
                kwargs.get('app_name', 'unknown'),)
        self._shared_request_params = kwargs

    def _get_request_params(self, **kwargs):
        """Merge shared params and new params."""
        request_params = copy.deepcopy(self._shared_request_params)
        for key, value in iteritems(kwargs):
            if isinstance(value, dict) and key in request_params:
                # ensure we don't lose dict values like headers or cookies
                request_params[key].update(value)
            else:
                request_params[key] = value
        return request_params

    def _sanitize_request_params(self, request_params):
        """Remove keyword arguments not used by `requests`"""
        if 'verify_ssl' in request_params:
            request_params['verify'] = request_params.pop('verify_ssl')
        return dict((key, val) for key, val in request_params.items()
                    if key in self._VALID_REQUEST_ARGS)

    def request(self, method, path, **kwargs):
        """Send a :class:`requests.Request` and demand a
        :class:`requests.Response`
        """
        if path:
            url = '%s/%s' % (self.url.rstrip('/'), path.lstrip('/'))
        else:
            url = self.url

        request_params = self._get_request_params(method=method,
                                                  url=url, **kwargs)
        request_params = self.pre_send(request_params)

        sanitized_params = self._sanitize_request_params(request_params)
        start_time = time.time()
        response = super(HTTPServiceClient, self).request(**sanitized_params)

        # Log request and params (without passwords)
        log.debug(
            '%s HTTP [%s] call to "%s" %.2fms',
            response.status_code, method, response.url,
            (time.time() - start_time) * 1000)
        auth = sanitized_params.pop('auth', None)
        log.debug('HTTP request params: %s', sanitized_params)
        if auth:
            log.debug('Authentication via HTTP auth as "%s"', auth[0])

        response.is_ok = response.status_code < 300
        if not self.is_acceptable(response, request_params):
            raise HTTPServiceError(response)
        response = self.post_send(response, **request_params)
        return response

    def pre_send(self, request_params):
        """Override this method to modify sent request parameters"""
        for adapter in itervalues(self.adapters):
            adapter.max_retries = request_params.get('max_retries', 0)

        return request_params

    def post_send(self, response, **kwargs):
        """Override this method to modify returned response"""
        return response

    def is_acceptable(self, response, request_params):
        """
        Override this method to create a different definition of
        what kind of response is acceptable.
        If `bool(the_return_value) is False` then an `HTTPServiceError`
        will be raised.

        For example, you might want to assert that the body must be empty,
        so you could return `len(response.content) == 0`.

        In the default implementation, a response is acceptable
        if and only if the response code is either
        less than 300 (typically 200, i.e. OK) or if it is in the
        `expected_response_codes` parameter in the constructor.
        """
        expected_codes = request_params.get('expected_response_codes', [])
        return response.is_ok or response.status_code in expected_codes
