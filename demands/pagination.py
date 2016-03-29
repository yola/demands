from itertools import count


PAGE_PARAM = 'page_param'
PAGE_SIZE_PARAM = 'page_size_param'
PAGE_SIZE = 'page_size'
PAGINATION_TYPE = 'pagination_type'


class PaginationType(object):
    ITEM = 'item'
    PAGE = 'page'


class PaginatedAPIIterator(object):
    """Paginated API iterator

    Provides an interator for items in a paginated function, useful for service
    methods that return paginated results.

    The paginated function accepts a page and page size argument and returns
    a page result for those arguments.

        >>> def numbers(page, page_size):
        ...    start = page * page_size
        ...    end = start + page_size
        ...    return range(0, 10)[start:end]
        ...
        >>> iterator = PaginatedAPIIterator(numbers)
        >>> list(iterator)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    The names of these arguments and value for `page_size` can be overriden
    through the init of the class:

        >>> def numbers(offset, length):
        ...     start = offset * length
        ...     end = start + length
        ...     return range(0, 100)[start:end]
        ...
        >>> PaginatedAPIIterator(
        ...     numbers, page_param='offset', page_size_param='length',
        ...     page_size=10)

    The `pagination_type` configuration defines how the api behaves, by
    default this is set to `PaginationType.PAGE` which means the API should
    expect the `page_param` to represent the index of the page to return.
    Set this value to `PaginationType.ITEM` if the API expects `page_param` to
    represent the index of an item.

        >>> def numbers(offset, limit):
        ...     start = offset
        ...     end = start + length
        ...     return range(0, 100)[start:end]
        ...
        >>> PaginationAPIIterator(
        ...     numbers, page_param='offset', 'page_size_param='limit',
        ...     pagination_type=PaginationType.ITEM)

    """
    DEFAULT_OPTIONS = {
        PAGE_PARAM: 'page',
        PAGE_SIZE_PARAM: 'page_size',
        PAGE_SIZE: 100,
        PAGINATION_TYPE: PaginationType.PAGE,
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
            for result in page:
                yield result
            if len(page) < self.options[PAGE_SIZE]:
                return

    def _get_page(self, page):
        kwargs = dict(self.kwargs)
        kwargs.update({
            self.options[PAGE_PARAM]: page,
            self.options[PAGE_SIZE_PARAM]: self.options[PAGE_SIZE],
        })
        return self.paginated_fn(*self.args, **kwargs)

    def _page_ids(self):
        if self.options[PAGINATION_TYPE] == PaginationType.PAGE:
            return count()
        if self.options[PAGINATION_TYPE] == PaginationType.ITEM:
            return count(0, self.options[PAGE_SIZE])
        raise ValueError('Unknown pagination_type')
