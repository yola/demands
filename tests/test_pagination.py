from unittest import TestCase

from demands.pagination import PaginatedAPIIterator


class PagitationTestsMixin(object):
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

    def test_get_by_index(self):
        self.responses = list(range(25))
        # first item
        self.assertEqual(self.psc[0], self.responses[0])
        # Non zero item
        self.assertEqual(self.psc[5], self.responses[5])
        # beyond first page item
        self.assertEqual(self.psc[20], self.responses[20])

    def test_get_by_index_raises_index_error_for_invalid_index(self):
        self.responses = list(range(25))
        with self.assertRaises(IndexError):
            self.psc[len(self.responses)]

    def test_get_by_slice(self):
        self.responses = list(range(25))
        # Same page, subset
        self.assertEqual(self.psc[0:5], self.responses[0:5])
        # Full page
        self.assertEqual(self.psc[0:10], self.responses[0:10])
        # Cross page
        self.assertEqual(self.psc[5:20], self.responses[5:20])
        # With step
        self.assertEqual(self.psc[0:20:2], self.responses[0:20:2])


class PagePaginationTest(TestCase, PagitationTestsMixin):
    def setUp(self):
        def get(url, page, page_size):
            start = page * page_size
            end = start + page_size
            return self.responses[start:end]

        self.psc = PaginatedAPIIterator(
            get, args=('http://example.net/',))
        self.psc.page_size = 10


class ItemPaginationTest(TestCase, PagitationTestsMixin):
    def setUp(self):
        def get(url, offset, limit):
            start = offset
            end = start + limit
            return self.responses[start:end]

        self.psc = PaginatedAPIIterator(
            get, args=('http://example.net/',))
        self.psc.page_size = 10
        self.psc.page_param = 'offset'
        self.psc.page_size_param = 'limit'
        self.psc.pagination_type = 'item'
