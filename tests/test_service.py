import os
import unittest2

import requests
from mock import Mock, patch

from demands.service import (Request, HTTPService, HTTPServiceError,
                             SYSTEM_CA_BUNDLE)


class PatchedRequestsTests(unittest2.TestCase):
    def setUp(self):
        self.requests_patcher = patch('demands.service.requests')
        self.requests = self.requests_patcher.start()
        self.response = Mock(spec=requests.Response, status_code=200,
                             content='', headers={'content-type': 'application/json'})

        for method in ('get', 'post', 'put', 'patch', 'delete'):
            fn = getattr(self.requests, method)
            fn.return_value = self.response

    def tearDown(self):
        self.requests_patcher.stop()


class RequestTests(PatchedRequestsTests):
    url = 'http://localhost/'

    def test_request_properly_authenticates(self):
        username, password = 'stevemcqueen', 'password'
        url = 'https://localhost/'
        request = Request(url, 'POST', None, None, None, True)
        request.authenticate(username, password)
        request.send()
        if os.path.isfile(SYSTEM_CA_BUNDLE):
            verify = SYSTEM_CA_BUNDLE
        else:
            verify = True
        self.requests.post.assert_called_once_with(
            url, headers={}, cookies={}, data={}, auth=(username, password),
            verify=verify)

    def test_request_sends_proper_arguments_for_headers_cookies_and_data(self):
        # Simple request
        request = Request(self.url, 'POST', None, None, None, False)
        request.send()
        self.requests.post.assert_called_with(self.url, headers={}, cookies={}, data={}, auth=None)

        # Request with headers
        headers = {'Content-Type': 'text/html'}
        request = Request(self.url, 'GET', None, headers, None, False)
        request.send()
        self.requests.get.assert_called_with(
            self.url, headers=headers, cookies={}, params={}, auth=None)

        # Request with data and cookies
        data = {'robots': 1}
        cookies = {'cookie_name': 'cookie_value'}
        request = Request(self.url, 'POST', data, None, cookies, False)
        request.send()
        self.requests.post.assert_called_with(self.url, data=data, headers={}, cookies=cookies, auth=None)


class HttpServiceTests(unittest2.TestCase):
    def setUp(self):
        self.service = HTTPService({
            'url': 'http://service.com/'
        })
        self.request = Request('http://service.com/', 'GET', None, None, None, False)
        self.response = Mock(headers={'content-type': 'text/plan'})

    def test_pre_send_triggers_authentication_when_username_provided(self):
        service = HTTPService({
            'url': 'http://localhost/',
            'username': 'foo',
            'password': 'bar'
        })
        service.pre_send(self.request)
        self.assertEqual(self.request.auth, ('foo', 'bar'))

    def test_pre_send_can_trigger_client_identification(self):
        service = HTTPService({
            'url': 'http://localhost/',
            'client_name': 'my_client',
            'client_version': '1.2.3',
            'app_name': 'my_app'
        })
        service.pre_send(self.request)
        self.assertEqual(self.request.headers['User-Agent'], 'my_client 1.2.3 - my_app')

    def test_post_send_raises_exception_in_case_of_error(self):
        self.response.configure_mock(status_code=500, content='content')
        self.assertRaises(HTTPServiceError, self.service.post_send, self.request, self.response)

    def test_post_send_do_not_raise_exception_in_case_of_expected_response_code(self):
        self.response.configure_mock(status_code=404, content='content')
        self.service.post_send(self.request, self.response, expected_response_codes=(404,))

    @patch('demands.service.log')
    def test_post_send_logs_errors(self, mock_log):
        """failed requests are logged with status code, and content"""
        self.response.configure_mock(status_code=500, content='content')
        with self.assertRaises(HTTPServiceError):
            self.service.post_send(self.request, self.response)
            error_msg = get_parsed_log_message(mock_log, 'error')
            self.assertIn('service.com', error_msg)
            self.assertIn('500', error_msg)
            self.assertIn('content', error_msg)


def get_parsed_log_message(mock_log, log_level):
    """Return the parsed log message sent to a mock log call at log_level

    Example:

        log = Mock()

        def do_something(data1, data2):
            log.info('Doing something with %s and %s', data1, data2)

        do_something('one', 'two')

        get_parsed_log_message(log, 'error')
        # => 'Doing something with one and two'

    """
    call_args = getattr(mock_log, log_level).call_args
    if not call_args:
        raise Exception('%s.%s was not called' % (mock_log, log_level))
    args, kwargs = call_args
    return args[0] % tuple(args[1:])
