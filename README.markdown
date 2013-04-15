# demands

Base class for building service clients on top of `requests` lib.  By default it
"demands" successful response from API endpoints, otherwise it raises exception.

Written and used by the folks at Yola. Check out our [free website][1] builder today.

## Overview

- HTTPService - base class for creating service clients, provides flexible way of http error handling
for descendants.  Supports pre|post-send hooks.
- Request - container for request related data
- HTTPServiceError - exception raised on unexpected service response

## Usage
    from demands import HTTPService

    class DummyService(HTTPService)
        def get_user(self, user_id):
            url = 'http://localhost/users/%s/' % user_id
            return self.get(url).json

        def safe_get_user(self, user_id, default_user):
            url = 'http://localhost/users/%s/' % user_id
            response = self.get(url, expected_response_codes=[404])
            return response.json if response.is_ok else default_user

## Testing

Install development requirements:

    pip install -r requirements.txt

Run the tests with:

    nosetests

[1]:https://www.yola.com/
