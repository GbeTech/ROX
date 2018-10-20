import unittest

from main import OrderBook, Order, ASK, BID
from util import generate_id, random_str, get_now


class TestOrderBook(unittest.TestCase):
    @staticmethod
    def create_mock_orderbook():
        """
        Creates a mock orderbook which contains two bids, and writes the data to <root>/logs/orderbook.log
        """
        order_book = OrderBook('test_log.log')
        # now = get_now()

        order_0 = Order(side=BID, price=100, size=10, id=generate_id())
        # order_0.timestamp = now - 10

        order_1 = Order(BID, 70, 15, generate_id())
        # order_1.timestamp = now - 5

        order_book.add_order(order_0, sender_id=random_str())
        order_book.add_order(order_1, random_str())

        return order_book

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.order_book = self.create_mock_orderbook()

    def test_add_ask(self):
        ask = Order(ASK, 99, 12, id=generate_id())
        self.order_book.add_order(ask, random_str())


if __name__ == '__main__':
    unittest.main()
else:
    print(__name__)