from itertools import count, islice


class PaginatedAPIIterator(object):
    """Paginated API iterator

    Provides an interator for items in a paginated function, useful for service
    methods that return paginated results. Supports indices and slicing.
    Negative indices are not supported.

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
        >>> iterator[10]
        9
        >>> iterator[0:5]
        [0, 1, 2, 3, 4]

    The names of these arguments and value for page_size can be overriden by
    extending this class:

        >>> class MyPaginatedAPIIterator(PaginatedAPIIterator):
        ...    page_parm = 'offset'
        ...    page_size_param = 'length'
        ...    page_size = 10
        ...
        >>> def numbers(offset, length):
        ...     start = offset * length
        ...     end = start + length
        ...     return range(0, 100)[start:end]
        ...
        >>> MyPaginatedAPIIterator(numbers)

    The pagination_type class variable defines how the api behaves, by default
    this is set to 'page' which means the API should expect the page_param to
    represent the index of the page to return. Set this value to 'item' if the
    API expects page_parm to represent the index of an item.
    """

    page_param = 'page'
    page_size_param = 'page_size'
    page_size = 100
    pagination_type = 'page'

    def __init__(self, paginated_fn, args=None, kwargs=None):
        self.paginated_fn = paginated_fn
        self.args = tuple(args or ())
        self.kwargs = dict(kwargs or {})
        self.pages = {}

    def __iter__(self):
        for page in self._page_ids():
            page = self._get_page(page)
            for result in page:
                yield result
            if len(page) < self.page_size:
                return

    def __getitem__(self, i):
        if isinstance(i, slice):
            return list(islice(self, i.start, i.stop, i.step))

        if self.pagination_type == 'page':
            page = i / self.page_size
            mod_i = i % self.page_size

        if self.pagination_type == 'item':
            page = i
            mod_i = 0

        return self._get_page(page)[mod_i]

    def _get_page(self, page):
        if page not in self.pages:
            kwargs = dict(self.kwargs)
            kwargs[self.page_param] = page
            kwargs[self.page_size_param] = self.page_size
            self.pages[page] = self.paginated_fn(*self.args, **kwargs)
        return self.pages[page]

    def _page_ids(self):
        if self.pagination_type == 'page':
            return count()
        if self.pagination_type == 'item':
            return count(0, self.page_size)
        raise ValueError('Unknown pagination_type')
