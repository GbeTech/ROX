import unittest

from main import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        order_book = OrderBook()