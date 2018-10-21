import unittest

from main import OrderBook, Order
from util import random_str


class TestOrderBook(unittest.TestCase):
    @staticmethod
    def create_bid(price, size):
        return Order(Order.BID, price, size)

    @staticmethod
    def create_ask(price, size):
        return Order(Order.ASK, price, size)

    def create_mock_orderbook(self):
        """
        Creates a mock orderbook which contains 4 bids (price, size):
        - (100, 10)
        - (70, 15)
        - (99, 7)
        - (101, 9)
        """
        order_book = OrderBook()
        order_book.add_order(self.create_bid(100, 10), sender_id=random_str())
        order_book.add_order(self.create_bid(70, 15), random_str())
        order_book.add_order(self.create_bid(99, 7), random_str())
        order_book.add_order(self.create_bid(101, 9), random_str())

        return order_book

    def test_add_ask_yes_bid_exhaust(self):
        order_book = self.create_mock_orderbook()
        # print("\n BEFORE")
        order_book.show_orderbook()
        _, min_bid_before = order_book.bids.min_item()
        _, max_bid_before = order_book.bids.max_item()
        self.assertEqual(order_book.bids.count, 4)
        self.assertEqual(order_book.asks.count, 0)
        self.assertEqual(min_bid_before.size, 15)
        self.assertEqual(min_bid_before.price, 70)
        self.assertEqual(max_bid_before.size, 9)
        self.assertEqual(max_bid_before.price, 101)

        order_book.add_order(self.create_ask(99, 26), random_str())
        # print("\n AFTER")
        # order_book.show_orderbook()

        self.assertEqual(order_book.bids.count, 1)
        self.assertEqual(order_book.asks.count, 0)

        _, min_bid_after = order_book.bids.min_item()
        self.assertEqual(min_bid_after.size, 15)
        self.assertEqual(min_bid_after.price, 70)
        self.assertEqual(min_bid_after, min_bid_before)

        self.assertIsNone(max_bid_before.size)
        self.assertTrue(max_bid_before.is_exhausted())

        _, max_bid_after = order_book.bids.max_item()
        self.assertEqual(max_bid_after, min_bid_after)
        self.assertNotEqual(max_bid_after, max_bid_before)

    def test_add_ask_no_bid_exhaust(self):
        order_book = self.create_mock_orderbook()
        # print("\n BEFORE")
        # order_book.pprint()
        min_bid_key, min_bid = order_book.bids.min_item()
        max_bid_key, max_bid = order_book.bids.max_item()
        self.assertEqual(order_book.bids.count, 4)
        self.assertEqual(order_book.asks.count, 0)
        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)
        self.assertEqual(max_bid.size, 9)
        self.assertEqual(max_bid.price, 101)

        order_book.add_order(self.create_ask(99, 8), random_str())
        # print("\n AFTER")
        # order_book.pprint()

        self.assertEqual(order_book.bids.count, 4)
        self.assertEqual(order_book.asks.count, 0)

        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)

        self.assertEqual(max_bid.size, 1)
        self.assertEqual(max_bid.price, 101)

    def test_show_orderbook(self):
        order_book = self.create_mock_orderbook()
        order_book.show_orderbook()

    def test_show_trades(self):
        from time import sleep
        order_book = self.create_mock_orderbook()
        for _ in range(26):
            order_book.add_order(self.create_ask(99, 1), random_str())
            sleep(0.1)

        trades = order_book.show_trades()
        trades_are_timestamp_sorted = all(
            [trade.timestamp < trades[i + 1].timestamp for i, trade in enumerate(trades[:-1])])
        self.assertTrue(trades_are_timestamp_sorted)


if __name__ == '__main__':
    unittest.main()