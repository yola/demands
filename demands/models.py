import logging
import time
import inspect

from urlparse import urljoin
from requests import Session


log = logging.getLogger(__name__)


class HTTPServiceError(Exception):
    def __init__(self, response):
        try:
            self.details = response.json()
        except ValueError:
            self.details = response.content
        super(Exception, self).__init__(
            'code: %s, details: %s' % (response.status_code, self.details)
        )


class HTTPService(Session):
    """Extendable base service client object"""

    def __init__(self, url, **kwargs):
        super(HTTPService, self).__init__()
        self.url = url
        self._shared_request_params = {}
        self._shared_request_params = self._get_request_params(**kwargs)

        if 'client_name' in kwargs:
            # client name and version is important because we want to
            # accurately log errors and throw deprecation warns when outdated
            headers = self._shared_request_params.get('headers') or {}
            headers.update({
                'User-Agent': '%s %s - %s' % (
                    kwargs.pop('client_name'),
                    kwargs.pop('client_version', 'x.y.z'),
                    kwargs.pop('app_name', 'unknown'),
                )
            })
            self._shared_request_params['headers'] = headers

    def _get_request_params(self, **kwargs):
        """Return a copy of self._shared_request_params updated with kwargs"""
        request_params = dict(self._shared_request_params)

        if 'username' in kwargs:
            username = kwargs.pop('username')
            request_params['auth'] = (username, kwargs.pop('password', None))
            log.debug('Authentication via HTTP auth as "%s"', username)

        request_params.update(kwargs)
        request_params = self._sanitize_request_params(request_params)
        return request_params

    def _sanitize_request_params(self, request_params):
        """Remove keyword arguments not used by `requests`"""
        valid_args = inspect.getargspec(Session.request)[0]
        return dict((key, val) for key, val in request_params.items()
                    if key in valid_args)

    def request(self, method, path, **kwargs):
        """"Configure params. Send a Request. Demand and return a Response."""
        url = urljoin(self.url, path)
        request_params = self._get_request_params(
            url=url, method=method, **kwargs)
        request_params = self.pre_send(request_params)

        start_time = time.time()
        response = super(HTTPService, self).request(**request_params)
        log.debug(
            '%s HTTP [%s] call to "%s" %.2fms',
            response.status_code, method, response.url,
            (time.time() - start_time) * 1000)
        log.debug('HTTP request params: %s', request_params)

        expected_codes = kwargs.get('expected_response_codes', [])
        response, expected_codes = self.post_send(response, expected_codes)
        self._demand_success(response, expected_codes)
        return response

    def pre_send(self, request_params):
        """"Override this method to modify sent request parameters"""
        return request_params

    def post_send(self, response, expected_response_codes):
        """"Override this method to modify returned response"""
        return response, expected_response_codes

    def _demand_success(self, response, expected_codes):
        response.is_ok = response.status_code < 300
        if not (response.is_ok or response.status_code in expected_codes):
            log.error(
                'Unexpected response from %s: url: %s, code: %s, details: %s',
                self.__class__.__name__, response.url, response.status_code,
                response.content)
            raise HTTPServiceError(response)
