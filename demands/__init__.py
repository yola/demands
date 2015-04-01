__doc__ = 'Base HTTP service client'
__version__ = '1.0.6'
__url__ = 'https://github.com/yola/demands'

import copy
import inspect
import json
import logging
import time

from requests import Session

log = logging.getLogger(__name__)


class HTTPServiceError(AssertionError):
    def __init__(self, response):
        self.response = response
        try:
            self.details = response.json()
        except ValueError:
            self.details = response.content
        super(AssertionError, self).__init__(
            'code: %s, details: %s' % (response.status_code, self.details)
        )


class HTTPServiceClient(Session):
    """Extendable base service client.

    Client can be configured with any param allowed by the requests API. These
    params will be uses with each and every request and can be overridden with
    kwargs.  `demands` adds the following params:

    :param expected_response_codes: (optional) Workaround for services which
        returns non-expected results, example: when search for users, and
        expect [] for when nobody is found, yet a 404 is returned.
    :param send_as_json: (optional) Encodes request data as json and sets
        'Content-Type' header.
    :param client_name: (optional) Sets the User-Agent header.  Important
        because we want to accurately log errors and throw deprecation
        warnings when clients are outdated
    :param client_version: (optional) Used with client_name
    :param app_name: (optional) Used with client_name
    :param cookies: (optional) Dict only, CookieJar not supported
    """

    _VALID_REQUEST_ARGS = inspect.getargspec(Session.request)[0]

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
        for key, value in kwargs.iteritems():
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
        """Sends a :class:`requests.Request` and demands
           a :class:`requests.Response`."""
        url = '%s/%s' % (self.url.rstrip('/'), path.lstrip('/'))
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

        response = self.post_send(response, **request_params)
        return response

    def _format_json_request(self, request_params):
        if request_params.get('send_as_json') and request_params.get('data'):
            request_params['data'] = json.dumps(
                request_params['data'],
                default=str
            )
            request_params.setdefault('headers', {})['Content-Type'] = (
                'application/json;charset=utf-8'
            )
        return request_params

    def pre_send(self, request_params):
        """Override this method to modify sent request parameters"""
        for adapter in self.adapters.itervalues():
            adapter.max_retries = request_params.get('max_retries', 0)
        return self._format_json_request(request_params)

    def post_send(self, response, **kwargs):
        """Override this method to modify returned response"""
        self._demand_success(response, kwargs)
        return response

    def _demand_success(self, response, request_params):
        expected_codes = request_params.get('expected_response_codes', [])
        response.is_ok = response.status_code < 300
        if not (response.is_ok or response.status_code in expected_codes):
            log.error(
                'Unexpected response from %s: url: %s, code: %s, details: %s',
                self.__class__.__name__, response.url, response.status_code,
                response.content)
            raise HTTPServiceError(response)
