import unittest2

import requests
from mock import Mock, patch

from demands.service import Request, HTTPService, HTTPServiceError


class PatchedRequestsTests(unittest2.TestCase):
    def setUp(self):
        self.requests_patcher = patch('demands.service.requests')
        self.requests = self.requests_patcher.start()
        self.response = Mock(spec=requests.Response, status_code=200,
                             content='',
                             headers={'content-type': 'application/json'})

        for method in ('get', 'post', 'put', 'patch', 'delete'):
            fn = getattr(self.requests, method)
            fn.return_value = self.response

    def tearDown(self):
        self.requests_patcher.stop()


class RequestTests(PatchedRequestsTests):
    url = 'http://localhost/'

    def test_minimal_post_request(self):
        """test minimal POST request"""
        request = Request(self.url, 'POST')
        request.send()
        self.requests.post.assert_called_with(
            self.url, auth=None, cookies={}, data={}, headers={},
            params={}, verify=False)

    def test_request_properly_authenticates(self):
        username, password = 'stevemcqueen', 'password'
        url = 'https://localhost/'
        request = Request(url, 'POST', verify=True)
        request.authenticate(username, password)
        request.send()
        self.requests.post.assert_called_once_with(
            url, auth=(username, password), cookies={}, data={}, headers={},
            params={}, verify=True)

    def test_post_request_headers(self):
        """test POST request headers"""
        headers = {'Content-Type': 'text/html'}
        request = Request(self.url, 'GET', headers=headers)
        request.send()
        self.requests.get.assert_called_with(
            self.url, auth=None, cookies={}, data={}, headers=headers,
            params={}, verify=False)

    def test_post_request_cookies_and_params(self):
        """test POST request cookies and params"""
        params = {'robots': 1}
        cookies = {'cookie_name': 'cookie_value'}
        request = Request(self.url, 'POST', cookies=cookies, params=params)
        request.send()
        self.requests.post.assert_called_with(
            self.url, auth=None, cookies=cookies, data={}, params=params,
            headers={}, verify=False)


class HttpServiceTests(unittest2.TestCase):
    def setUp(self):
        self.service = HTTPService({
            'url': 'http://service.com/'
        })
        self.request = Request('http://service.com/', 'GET')
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
        self.assertEqual(
            self.request.headers['User-Agent'], 'my_client 1.2.3 - my_app')

    def test_post_send_raises_exception_in_case_of_error(self):
        self.response.configure_mock(status_code=500, content='content')
        self.assertRaises(
            HTTPServiceError, self.service.post_send, self.request,
            self.response)

    def test_post_send_raises_exception_with_details_on_error(self):
        self.response.configure_mock(status_code=500, content='content')
        with self.assertRaises(HTTPServiceError) as e:
            self.service.post_send(self.request, self.response)
        self.assertEqual(e.exception.code, 500)
        self.assertEqual(e.exception.details, 'content')

    def test_post_sends_no_exception_in_case_of_expected_response_code(self):
        self.response.configure_mock(status_code=404, content='content')
        self.service.post_send(
            self.request, self.response, expected_response_codes=(404,))

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
