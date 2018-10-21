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
        Creates a mock orderbook which contains two bids, and writes the data to <root>/logs/orderbook.log
        """
        order_book = OrderBook()
        order_book.add_order(self.create_bid(100, 10), sender_id=random_str())
        order_book.add_order(self.create_bid(70, 15), random_str())
        order_book.add_order(self.create_bid(99, 7), random_str())
        order_book.add_order(self.create_bid(101, 9), random_str())

        return order_book

    def test_add_ask_not_satisfied(self):
        print("\n BEFORE")
        order_book = self.create_mock_orderbook()
        order_book.pprint()
        min_bid_key, min_bid = order_book.bids.min_item()
        max_bid_key, max_bid = order_book.bids.max_item()
        self.assertEqual(order_book.bids.count, 4)
        self.assertEqual(order_book.asks.count, 0)
        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)
        self.assertEqual(max_bid.size, 9)
        self.assertEqual(max_bid.price, 101)

        order_book.add_order(self.create_ask(99, 26), random_str())
        print("\n AFTER")
        order_book.pprint()

        self.assertEqual(order_book.bids.count, 1)
        self.assertEqual(order_book.asks.count, 0)

        min_bid_key, min_bid = order_book.bids.min_item()
        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)

        print(max_bid)
        self.assertIsNone(max_bid.size)
        self.assertTrue(max_bid.is_exhausted())

        max_bid_key, max_bid = order_book.bids.max_item()
        self.assertEqual(max_bid, min_bid)
        # self.assertEqual(max_bid.price, 101)

    def test_add_ask_satisfied(self):
        # print("\n BEFORE")
        order_book = self.create_mock_orderbook()
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


if __name__ == '__main__':
    unittest.main()