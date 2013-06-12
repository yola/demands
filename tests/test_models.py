import unittest2
import inspect

from requests import Session, Response
from mock import Mock, patch

from demands.models import HTTPService, HTTPServiceError


class PatchedSessionTests(unittest2.TestCase):
    def setUp(self):
        # must patch inspect since it is used on Session.request, and when
        # Session.request is mocked, inspect blows up
        self.request_args = inspect.getargspec(Session.request)
        self.inspect_patcher = patch('demands.models.inspect.getargspec')
        self.patched_inspect = self.inspect_patcher.start()
        self.patched_inspect.return_value = self.request_args

        self.request_patcher = patch.object(Session, 'request')
        self.request = self.request_patcher.start()
        self.response = Mock(spec=Response(), status_code=200)
        self.request.return_value = self.response

    def tearDown(self):
        self.request_patcher.stop()
        self.inspect_patcher.stop()


class HttpServiceTests(PatchedSessionTests):

    def setUp(self):
        PatchedSessionTests.setUp(self)
        self.service = HTTPService('http://service.com/')

    def test_returning_responses_from_all_session_calls(self):
        self.assertEqual(self.service.get('/path'), self.response)
        self.assertEqual(self.service.put('/path'), self.response)
        self.assertEqual(self.service.delete('/path'), self.response)
        self.assertEqual(self.service.post('/path'), self.response)
        self.assertEqual(self.service.patch('/path'), self.response)
        self.assertEqual(self.service.options('/path'), self.response)
        self.assertEqual(self.service.head('/path'), self.response)

    def test_get_request_with_params(self):
        """GET request with url parameters"""
        self.service.get('/get-endpoint', params={'foo': 'bar'})
        self.request.assert_called_with(
            method='GET', url='http://service.com/get-endpoint',
            allow_redirects=True, params={'foo': 'bar'})

    def test_minimal_post_request(self):
        """minimal POST request"""
        self.service.post('/post-endpoint')
        self.request.assert_called_with(
            method='POST', url='http://service.com/post-endpoint', data=None)

    def test_minimal_put_request(self):
        """minimal PUT request"""
        self.service.put('/put-endpoint')
        self.request.assert_called_with(
            method='PUT', url='http://service.com/put-endpoint', data=None)

    def test_minimal_delete_request(self):
        """minimal DELETE request"""
        self.service.delete('/delete-endpoint')
        self.request.assert_called_with(
            method='DELETE', url='http://service.com/delete-endpoint')

    def test_sets_authentication_when_username_provided(self):
        service = HTTPService(
            url='http://localhost/',
            username='foo',
            password='bar',
        )
        service.get('/authed-endpoint')
        self.request.assert_called_with(
            method='GET', url='http://localhost/authed-endpoint',
            allow_redirects=True, auth=('foo', 'bar'))

    def test_client_identification_adds_user_agent_header(self):
        """client identification adds User-Agent header"""
        service = HTTPService(
            url='http://localhost/',
            client_name='my_client',
            client_version='1.2.3',
            app_name='my_app',
        )
        service.get('/test')
        self.request.assert_called_with(
            method='GET', url='http://localhost/test', allow_redirects=True,
            headers={'User-Agent': 'my_client 1.2.3 - my_app'})

    def test_post_send_raise_exception_in_case_of_error(self):
        self.response.configure_mock(url='http://broken/', status_code=500)
        with self.assertRaises(HTTPServiceError):
            self.service.request('METHOD', 'http://broken/')

    def test_post_send_raises_exception_with_details_on_error(self):
        self.response.configure_mock(
            status_code=500, content='content', url='http://broken/')
        with self.assertRaises(HTTPServiceError) as e:
            self.service.request('METHOD', 'http://broken/')
            self.assertEqual(e.exception.code, 500)
            self.assertEqual(e.exception.details, 'content')

    def test_post_sends_no_exception_in_case_of_expected_response_code(self):
        self.response.configure_mock(
            status_code=404, content='content', url='http://notfound/')
        self.service.request(
            'METHOD', 'http://notfound/', expected_response_codes=(404,))

    @patch('demands.models.log')
    def test_post_send_logs_errors(self, mock_log):
        """failed requests are logged with status code, and content"""
        self.response.configure_mock(
            status_code=500, content='content', url='http://service.com/')
        with self.assertRaises(HTTPServiceError):
            self.service.request('METHOD', 'http://service.com/')
            error_msg = get_parsed_log_message(mock_log, 'error')
            self.assertIn('service.com', error_msg)
            self.assertIn('500', error_msg)
            self.assertIn('content', error_msg)

    def test_santization_of_request_parameters_removes_unknowns(self):
        lots_of_params = {
            'expected_response_codes': (404,),
            'method': 'METHOD',
            'something_odd': True
        }
        self.assertEqual(
            self.service._sanitize_request_params(lots_of_params),
            {'method': 'METHOD'})


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
