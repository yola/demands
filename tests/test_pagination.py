from unittest import TestCase

from demands.pagination import PaginatedAPIIterator, PaginationType


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

        start = page * page_size
        end = start + page_size

        return super(PagePaginationTest, self).get(start, end, *args, **kwargs)

    def setUp(self):
        self.psc = PaginatedAPIIterator(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10)


class ItemPaginationTest(TestCase, PaginationTestsMixin):
    def get(self, *args, **kwargs):
        start = kwargs.pop('offset')
        end = start + kwargs.pop('limit')
        return super(ItemPaginationTest, self).get(start, end, *args, **kwargs)

    def setUp(self):
        self.psc = PaginatedAPIIterator(
            self.get, args=self.args, kwargs=self.kwargs, page_size=10,
            page_param='offset', page_size_param='limit',
            pagination_type=PaginationType.ITEM)
