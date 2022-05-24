from itertools import count


PAGE_PARAM = 'page_param'
PAGE_SIZE_PARAM = 'page_size_param'
PAGE_SIZE = 'page_size'
PAGINATION_TYPE = 'pagination_type'
RESULTS_KEY = 'results_key'
NEXT_KEY = 'next_key'
START = 'start'


class PaginationType(object):
    ITEM = 'item'
    PAGE = 'page'


class PaginatedResults(object):
    """Paginated API results

    Returns an iteratable container of items from paginated function, useful
    for service methods that return paginated results.

    The paginated function should accept a page and page size argument and
    return a page of results for those arguments nested in a 'results' key:

        >>> def numbers(page, page_size):
        ...    start = (page - 1) * page_size
        ...    end = start + page_size
        ...    return {'results': range(0, 100)[start:end]}
        ...
        >>> results = PaginatedResults(numbers)
        >>> list(results)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, ... 99]

    The names of these arguments, the value for `page_size`, the starting page
    number (which defaults to page 1), and the results key can be overriden
    through the init of the class:

        >>> def numbers(offset, length):
        ...     start = offset * length  # expects start of 0
        ...     end = start + length
        ...     return {'numbers': range(0, 100)[start:end]}
        ...
        >>> results = PaginatedResults(
        ...     numbers, page_param='offset', page_size_param='length',
        ...     page_size=10, results_key='numbers', start=0)
        >>> [n for n in results]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, ... 99]

    If your function returns the results as a top-level list, set the
    `results_key` to `None`.

        >>> def numbers(page, page_size):
        ...    start = (page - 1) * page_size
        ...    end = start + page_size
        ...    return range(0, 100)[start:end]
        ...
        >>> results = PaginatedResults(numbers, results_key=None)
        >>> list(results)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, ... 99]

    The `pagination_type` configuration defines how the api behaves, by
    default this is set to `PaginationType.PAGE` which means the API should
    expect the `page_param` to represent the index of the page to return.
    Set this value to `PaginationType.ITEM` if the API expects `page_param` to
    represent the index of an item.

        >>> def numbers(offset, limit):
        ...     start = offset
        ...     end = start + limit
        ...     return {'results': range(0, 100)[start:end]}
        ...
        >>> results = PaginatedResults(
        ...     numbers, page_param='offset', page_size_param='limit',
        ...     pagination_type=PaginationType.ITEM)
        >>> list(results)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, ... 99]

    """
    DEFAULT_OPTIONS = {
        PAGE_PARAM: 'page',
        PAGE_SIZE_PARAM: 'page_size',
        PAGE_SIZE: 100,
        PAGINATION_TYPE: PaginationType.PAGE,
        RESULTS_KEY: 'results',
        NEXT_KEY: 'next',
    }

    def __init__(self, paginated_fn, args=(), kwargs=None, **options):
        self.paginated_fn = paginated_fn
        self.args = args
        self.kwargs = kwargs or {}
        self.options = dict(self.DEFAULT_OPTIONS)
        self.options.update(options)

    def __iter__(self):
        for page_id in self._page_ids():
            page = self._get_page(page_id)
            for item in page.items:
                yield item
            if page.is_last_page:
                return

    def _get_page(self, page):
        kwargs = dict(self.kwargs)
        kwargs.update({
            self.options[PAGE_PARAM]: page,
            self.options[PAGE_SIZE_PARAM]: self.options[PAGE_SIZE],
        })
        one_page_data = self.paginated_fn(*self.args, **kwargs)
        return Page(one_page_data, self.options)

    def _page_ids(self):
        if self.options[PAGINATION_TYPE] == PaginationType.PAGE:
            start = self.options.get(START, 1)
            return count(start)
        if self.options[PAGINATION_TYPE] == PaginationType.ITEM:
            start = self.options.get(START, 0)
            return count(start, self.options[PAGE_SIZE])
        raise ValueError('Unknown pagination_type')


class Page(object):
    def __init__(self, data, options):
        self._data = data
        self._options = options

    @property
    def items(self):
        results_key = self._options.get(RESULTS_KEY)
        if results_key:
            return self._data[results_key]
        return self._data

    @property
    def size(self):
        return len(self.items)

    @property
    def is_last_page(self):
        next_key = self._options.get(NEXT_KEY)

        if next_key in self._data:
            return self._data[next_key] is None

        return self.size < self._options[PAGE_SIZE]
