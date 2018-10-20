import unittest

from main import OrderBook, Order, ASK, BID
from util import generate_id, random_str, epoch
from random import randint


class TestOrderBook(unittest.TestCase):
    @staticmethod
    def create_mock_orderbook():
        """
        Creates a mock orderbook which contains two bids, and writes the data to <root>/logs/orderbook.log
        """
        order_book = OrderBook()
        now = epoch()

        order0 = Order(timestamp=now - 10, side=BID, size=100, price=10, id=generate_id())
        order_book.add_order(order0, sender_id=random_str())
        order_book.add_order(Order(now - 5, BID, 70, 15, generate_id()), random_str())

        # with open('./logs/orderbook.log', 'w') as f:
        #     f.write(order_book.to_log())
        return 0
        # bid_id = generate_id()

        # create a few bids in the past, each 5 seconds apart
        # bid_time = epoch() - 5 * (i + 1)
        # bid = Order(bid_time, BID, 100, 10, bid_id)
        # order_book.add_order(bid, random_str())

    def setUp(self):
        order_book = self.create_mock_orderbook()

    def test_something(self):
        self.assertEqual(5, 5)