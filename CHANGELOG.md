# [Changelog](https://github.com/yola/demands/releases)

## 4.0.0

* Rename `PaginatedAPIIterator` to `PaginatedResults`.
* Remove JSONServiceClient. Newest `requests` version provides functionality
  that obviates the need for it.

## 3.0.0

* Add decoding of json responses to JSONServiceClient

## 2.0.0

* Add JSONServiceClient
* Remove `send_as_json` configuration for HTTPServiceClient
* Changes to PaginatedAPIIterator:
    * Default start page is 1 for page-based pagination (was 0)
    * Expects the paginated function to return a dict with a `'results'` key
    * See PaginatedAPIIterator docstring for customizing those behaviors

## 1.3.1

* Add MANIFEST.in

## 1.3.0 - Broken

* Add PaginatedAPIIterator, helper utility for paginated service methods

## 1.2.0

* Allow the user to customise the definition of an acceptable response by overriding `is_acceptable`.
* Exceptions are now raised directly by `request` if `is_acceptable()` returns `False` instead of in the default
`post_send`.

## 1.1.5

* No change: a broken version of 1.1.4 was released accidentally (files were missing from the package).

## 1.1.4

* Stop logging an error for unsuccessful responses. Move the information
  from the logging statement to the exception message.

## 1.1.3

* Make Demands work correctly if `path` param is empty. Don't add slash to
  the base URL in this case.

## 1.1.0

* Add Python 3 support

## 1.0.6

* Switch to version `requests` >= `2.4.2`

## 1.0.5

* Allows to set max retries

## 1.0.4

* Accept param `verify_ssl` as an alias for `verify`
* Fix easy_install error, a pitfall of using `__init__.py`

## 1.0.3

* Adds API documentation
* Add a license

## 1.0.2

* Adds http response as property of HTTPServiceError exception
* HTTPServiceError now subclasses AssertionError instead of IOError

## 1.0.1

* Fixes issue with composing url

## 1.0.0

* HTTPServiceClient invoked with arguments instead of a dictionary
* Enable and match parameters used by `requests`

    Before
    * `data`, used for both query string and request body
    * `verify_ssl`

    Now
    * `params`: dictionary or bytes to be sent in the query string
    * `data`: dictionary, bytes, or file-like object to send in the body
    * `verify`: verify the SSL cert

## 0.2.1

* Save error response content in HTTPServiceError exception

## 0.2.0

* Switches to requests > 1.0.0

## 0.1.0

* Adds client identification
* Provides an easier way to modify request arguments in pre_send()

## 0.0.1

* Initial version
