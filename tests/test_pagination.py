from unittest import TestCase

from demands.pagination import PaginatedResults, PaginationType


class PaginationTestsMixin(object):
    args = (1, 2, 3)
    kwargs = {'one': 1, 'two': 2}

    def get(self, start, end, *args, **kwargs):
        self.assertEqual(args, self.args)
        self.assertEqual(kwargs, self.kwargs)
        return self.responses[start:end]

    def test_iterate_one_undersized_page(self):
        self.responses = list(range(5))
        r = list(self.psc)
        self.assertEqual(r, self.responses)

    def test_iterate_multiple_full_pages(self):
        self.responses = list(range(20))
        r = list(self.psc)
        self.assertEqual(r, self.responses)

    def test_iterate_multiple_pages(self):
        self.responses = list(range(25))
        r = list(self.psc)
        self.assertEqual(r, self.responses)


class PagePaginationTest(TestCase, PaginationTestsMixin):
    def get(self, *args, **kwargs):
        page = kwargs.pop('page')
        page_size = kwargs.pop('page_size')

        start = (page - 1) * page_size
        end = start + page_size

        return super(PagePaginationTest, self).get(start, end, *args, **kwargs)

    def setUp(self):
        self.psc = PaginatedResults(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10,
            results_key=None)


class PagePaginationTestWithNestedResults(PagePaginationTest):
    def get(self, *args, **kwargs):
        results = super(PagePaginationTestWithNestedResults, self).get(
            *args, **kwargs)
        return {'results': results}

    def setUp(self):
        self.psc = PaginatedResults(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10)


class ItemPaginationTest(TestCase, PaginationTestsMixin):
    def get(self, *args, **kwargs):
        start = kwargs.pop('offset')
        end = start + kwargs.pop('limit')
        return super(ItemPaginationTest, self).get(start, end, *args, **kwargs)

    def setUp(self):
        self.psc = PaginatedResults(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10,
            page_param='offset', page_size_param='limit',
            pagination_type=PaginationType.ITEM, results_key=None)


class ItemPaginationTestWithNestedResults(ItemPaginationTest):
    def get(self, *args, **kwargs):
        results = super(ItemPaginationTestWithNestedResults, self).get(
            *args, **kwargs)
        return {'results': results}

    def setUp(self):
        self.psc = PaginatedResults(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10,
            page_param='offset', page_size_param='limit',
            pagination_type=PaginationType.ITEM)


class ItemPaginationTestWithNestedResultsAndNextLink(TestCase):
    def setUp(self):
        self.psc = PaginatedResults(
            self.get, page_size=10,
            page_param='offset', page_size_param='limit',
            pagination_type=PaginationType.ITEM, next_key='next_page')

    def get(self, *args, **kwargs):
        # Emulate 5 full pages (offset 0-4), then emulate error.
        offset = kwargs['offset']
        if offset > 4 * 10:
            raise ValueError('No Data')

        next = 'next_url' if offset < 4 * 10 else None
        return {'results': list(
            range(offset, offset + kwargs['limit'])), 'next_page': next}

    def test_iteration_stops_on_empty_next(self):
        self.assertEqual(list(self.psc), list(range(0, 50)))
