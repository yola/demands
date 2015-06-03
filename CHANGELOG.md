# [Changelog](https://github.com/yola/demands/releases)

## 1.0.7

* Use fixed "Accept" header - "application/json"

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
