Demands
=======

|Build Status| |Coverage Status| |Latest Version| |Downloads|

A base HTTP service client.

By default it "demands" successful responses from API endpoints,
otherwise it raises an exception.

Demands accepts all the same parameters as ``requests.request`` and
extends the ``requests.Session`` class, documentation for both:
`Requests Developer
Interface <http://www.python-requests.org/en/latest/api/>`__.

Written and used by the folks at Yola to support our `free website
builder <https://www.yola.com/>`__.

HTTPServiceClient Overview
--------------------------

-  base class for creating service clients
-  provides flexible way of http error handling for descendants
-  ``HTTPServiceError`` raised on unexpected service response

-  Supports pre-send and post-send hooks

Usage
-----

.. code:: python

    from demands import HTTPServiceClient

    class MyService(HTTPServiceClient):
        def get_user(self, user_id):
            return self.get('/users/%s/' % user_id).json()

        def safe_get_user(self, user_id, default_user):
            response = self.get(
                '/users/%s/' % user_id, 
                expected_response_codes=[404])
            return response.json() if response.is_ok else default_user


    service = MyService(url='http://localhost/')
    user = service.get_user(1234)

Any parameters passed to the constructor will also be used for each and
every request:

.. code:: python

    service = MyService(
        url='http://localhost/',
        headers={'h1':'value'},
        auth=('username','pass'),
    )

    # sent with auth and both headers
    user = service.get('/some-path', headers={'h2': 'kittens'})

Testing
-------

Install development requirements:

::

    pip install -r requirements.txt

Run the tests with:

::

    nosetests

API documentation
-----------------

To generate the documentation:

::

    cd docs && PYTHONPATH=.. make singlehtml

.. |Build Status| image:: https://img.shields.io/travis/yola/demands.svg
   :target: https://travis-ci.org/yola/demands
.. |Coverage Status| image:: https://img.shields.io/coveralls/yola/demands.svg
   :target: https://coveralls.io/r/yola/demands?branch=master
.. |Latest Version| image:: https://img.shields.io/pypi/v/demands.svg
   :target: https://pypi.python.org/pypi/demands/
.. |Downloads| image:: https://img.shields.io/pypi/dm/demands.svg
   :target: https://pypi.python.org/pypi/demands/
