# demands

demands is a base HTTP service client class on top of [requests][2].

By default it "demands" successful responses from API endpoints,
otherwise it raises an exception.

Written and used by the folks at Yola to support our [free website builder][1].

## Overview

- HTTPServiceClient - base class for creating service clients, provides flexible way of http error handling
for descendants.  Supports pre- and post-send hooks.
- HTTPServiceError - exception raised on unexpected service response

## Usage
```python
from demands import HTTPService

class DummyService(HTTPService):
    def get_user(self, user_id):
        url = 'http://localhost/users/%s/' % user_id
        return self.get(url).json

    def safe_get_user(self, user_id, default_user):
        url = 'http://localhost/users/%s/' % user_id
        response = self.get(url, expected_response_codes=[404])
        return response.json if response.is_ok else default_user
```

Helpful to know the [requests developer interface](https://requests.readthedocs.org/en/latest/api/).

## Testing

Install development requirements:

    pip install -r requirements.txt

Run the tests with:

    nosetests

[1]:https://www.yola.com/
[2]:https://github.com/kennethreitz/requests
