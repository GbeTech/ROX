import unittest

from main import OrderBook, Order
from util import random_str
import logging
import os
import re

TESTS_FOLDER_NAME = 'tests'
# Change current working directory to <root> and not /tests
# All file paths assume working dir is root
cwd = os.getcwd()
m = re.fullmatch(f'.*{TESTS_FOLDER_NAME}$', cwd)
if m:
    split = os.path.split(cwd)
    os.chdir(split[0])


class TestOrderBook(unittest.TestCase):
    REMOVE_LOG_FILES = False  # set True to delete all log files created by the tests after done running

    @classmethod
    def tearDownClass(cls):
        """After all tests are done, deletes all logs created by the tests if REMOVE_LOG_FILES == True"""
        super().tearDownClass()
        if not cls.REMOVE_LOG_FILES:
            return
        for _, _, testfiles in os.walk(TESTS_FOLDER_NAME):
            for file in testfiles:
                test_logfile = re.fullmatch(r'^test_[a-z_]*\.log$', file)
                if test_logfile:
                    # file is a test log file created by one of the test methods
                    os.remove(os.path.join(TESTS_FOLDER_NAME, test_logfile.group(0)))

    @staticmethod
    def create_bid(price, size):
        return Order(Order.BID, price, size)

    @staticmethod
    def create_ask(price, size):
        return Order(Order.ASK, price, size)

    def create_mock_orderbook(self, logfile_full_path):
        """
        Creates a mock orderbook which contains 4 bids (price, size):
        - (100, 10)
        - (70, 15)
        - (99, 7)
        - (101, 9)
        These hardcoded values are tested throughout the testing functions, don't change
        """
        order_book = OrderBook(logfile_full_path)
        order_book.add_order(self.create_bid(100, 10), sender_id=random_str())
        order_book.add_order(self.create_bid(70, 15), random_str())
        order_book.add_order(self.create_bid(99, 7), random_str())
        order_book.add_order(self.create_bid(101, 9), random_str())

        return order_book

    def tearDown(self):
        """Since:
        1) OrderBook methods are likely to write to a log file, and
        2) Using logging std lib, the same log file is shared across modules and files, and
        3) Some tests here test the actual output of the logging mechanism,
        Each different test writes to a different log file (under /tests).
        """
        super().tearDown()
        current_logger = logging.getLogger()
        handler = current_logger.handlers[0]
        handler.close()
        current_logger.removeHandler(handler)

    def test_add_ask_yes_bid_exhaust(self):
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')
        _, min_bid_before = order_book.bids.min_item()
        _, max_bid_before = order_book.bids.max_item()
        self.assertEqual(order_book.bids.count, 4)
        self.assertEqual(order_book.asks.count, 0)
        self.assertEqual(min_bid_before.size, 15)
        self.assertEqual(min_bid_before.price, 70)
        self.assertEqual(max_bid_before.size, 9)
        self.assertEqual(max_bid_before.price, 101)

        order_book.add_order(self.create_ask(99, 26), random_str())

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
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')

        min_bid_key, min_bid = order_book.bids.min_item()
        max_bid_key, max_bid = order_book.bids.max_item()
        self.assertEqual(order_book.bids.count, 4)
        self.assertTrue(order_book.asks.is_empty())
        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)
        self.assertEqual(max_bid.size, 9)
        self.assertEqual(max_bid.price, 101)

        order_book.add_order(self.create_ask(99, 8), random_str())

        self.assertEqual(order_book.bids.count, 4)
        self.assertTrue(order_book.asks.is_empty())

        self.assertEqual(min_bid.size, 15)
        self.assertEqual(min_bid.price, 70)

        self.assertEqual(max_bid.size, 1)
        self.assertEqual(max_bid.price, 101)

    def test_show_orderbook(self):
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')
        output = order_book.show_orderbook()
        lines = output.splitlines()

        regex = ['^$',
                 '^Bids:$',
                 '^\(0\) timestamp: \d{10}\.\d{5,7}, side: b, price: 70, size: 15, id: \d{13}, sender_id: "[a-zA-Z0-9]{8}"',
                 '^\(1\) timestamp: \d{10}\.\d{5,7}, side: b, price: 99, size: 7, id: \d{13}, sender_id: "[a-zA-Z0-9]{8}"',
                 '^\(2\) timestamp: \d{10}\.\d{5,7}, side: b, price: 100, size: 10, id: \d{13}, sender_id: "[a-zA-Z0-9]{8}"',
                 '^\(3\) timestamp: \d{10}\.\d{5,7}, side: b, price: 101, size: 9, id: \d{13}, sender_id: "[a-zA-Z0-9]{8}"',
                 '^Asks:$',
                 '-- No asks --',
                 ]

        for i, line in enumerate(lines):
            self.assertRegex(line, regex[i])

        # remove all bids
        for bid in list(order_book.bids.values()):
            order_book.remove_order(bid.id, bid.sender_id)

        regex = ['^$',
                 '^Bids:$',
                 '-- No bids --',
                 '^Asks:$',
                 '-- No asks --',
                 ]

        for i, line in enumerate(order_book.show_orderbook().splitlines()):
            self.assertRegex(line, regex[i])

    def test_show_trades(self):
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')
        for _ in range(26):
            order_book.add_order(self.create_ask(99, 1), random_str())

        trades = order_book.show_trades()
        trades_are_timestamp_sorted = all(
            [trade.timestamp < trades[i + 1].timestamp for i, trade in enumerate(trades[:-1])])
        self.assertTrue(trades_are_timestamp_sorted)

    def test_remove_order(self):
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')
        ask = self.create_ask(100, 30)
        order_book.add_order(ask, random_str())
        self.assertEqual(order_book.asks.count, 1)
        self.assertEqual(order_book.bids.count, 3)
        order_book.remove_order(ask.id, ask.sender_id)
        self.assertEqual(order_book.asks.count, 0)

        # Copy the values, so removing their references won't interfere with testing
        bids_copy = list(order_book.bids.values())
        bids_ids = [bid.id for bid in bids_copy]

        for bid_id in bids_ids:
            # Should not remove orders with no matching sender id.
            order_book.remove_order(bid_id, "BAD SENDER ID")

        self.assertEqual(order_book.bids.count, 3)  # no bids_copy were removed

        for bid in bids_copy:
            # Should remove
            order_book.remove_order(bid.id, bid.sender_id)

        self.assertEqual(order_book.bids.count, 0)

    def test_logger(self):
        new_log_file = f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log'
        order_book = OrderBook(new_log_file)
        bid_sender_id = random_str()
        order_book.add_order(self.create_bid(100, 5), bid_sender_id)
        ask_sender_id = random_str()
        order_book.add_order(self.create_ask(90, 7), ask_sender_id)
        with open(new_log_file, 'r') as f:
            lines = f.readlines()
            # the data in the now created log file is expected to match the following regex expressions
            regex = [['BID \| timestamp: \d{10}\.\d{5,7}',
                      '^side: b$',
                      '^price: 100$',
                      '^size: 5$',
                      'id: \d{13}',
                      f'sender_id: "{bid_sender_id}"'],
                     ['ASK \| timestamp: \d{10}\.\d{5,7}',
                      '^side: a$',
                      '^price: 90$',
                      '^size: 7$',
                      'id: \d{13}',
                      f'sender_id: "{ask_sender_id}"'],
                     ['TRADE \| timestamp: \d{10}\.\d{5,7}',
                      '^price: 100$',
                      '^size: 5$',
                      f'buyer_id: "{bid_sender_id}"',
                      f'seller_id: "{ask_sender_id}"'],
                     ['\t--> ASK id: \d{13} now has size: 2'],
                     ['\t--> BID id: \d{13} now has been exhausted']]
            for i, line in enumerate(lines):
                for j, order_prop in enumerate(line.split(', ')):
                    self.assertRegex(order_prop, regex[i][j])


if __name__ == '__main__':
    unittest.main()