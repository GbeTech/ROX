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
        
        if not current_logger.handlers:
            # "test_bad_order_side()" doesn't instanciate an OrderBook
            # so no logging is done == no handlers to close and remove
            return
        
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
        
        regex = list(map(re.compile, ('^$',
                                      '^Bids:$',
                                      r'^\(0\) timestamp: \d{10}\.\d{5,7}, side: b, price: 70, size: 15, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                                      r'^\(1\) timestamp: \d{10}\.\d{5,7}, side: b, price: 99, size: 7, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                                      r'^\(2\) timestamp: \d{10}\.\d{5,7}, side: b, price: 100, size: 10, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                                      r'^\(3\) timestamp: \d{10}\.\d{5,7}, side: b, price: 101, size: 9, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                                      '^Asks:$',
                                      '-- No asks --',
                                      )
                         ))
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
        import time
        order_book = self.create_mock_orderbook(f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log')
        for _ in range(26):
            order_book.add_order(self.create_ask(99, 1), random_str())
            time.sleep(0.01)
        
        trades = order_book.show_trades()
        trades_are_timestamp_sorted = all(
                [trade.timestamp < trades[i + 1].timestamp for i, trade in enumerate(trades[:-1])])
        self.assertTrue(trades_are_timestamp_sorted)
    
    def test_show_top(self):
        new_log_file = f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log'
        order_book = OrderBook(new_log_file)
        order_book.add_order(self.create_ask(100, 30), random_str())
        order_book.add_order(self.create_ask(100, 29), random_str())
        order_book.add_order(self.create_bid(10, 3), random_str())
        order_book.add_order(self.create_bid(10, 4), random_str())
        
        highest_bid, lowest_ask = order_book.show_top()
        
        # Test overridden Order comparison functions (by _key())
        self.assertTrue((highest_bid.price, highest_bid.size), (10, 4))
        self.assertTrue((lowest_ask.price, lowest_ask.size), (100, 29))
        
        order_book.add_order(self.create_ask(99, 28), random_str())
        order_book.add_order(self.create_bid(11, 5), random_str())
        
        highest_bid, lowest_ask = order_book.show_top()
        self.assertTrue((highest_bid.price, highest_bid.size), (11, 5))
        self.assertTrue((lowest_ask.price, lowest_ask.size), (99, 28))
    
    def test_order_size_setter(self):
        order = Order("a", 100, 5)
        order.size = -5
        self.assertIsNone(order.size)
        self.assertTrue(order.is_exhausted())
    
    def test_bad_order_side(self):
        bad_side = "not a nor b"
        err_regex = '\n'.join([
            f'^Tried to initialize Order instance with illegal order side arg: "{bad_side}"\.',
            'Only "b" or "a" allowed\.$'
            ])
        with self.assertRaisesRegex(ValueError, err_regex):
            Order(bad_side, 100, 5)
    
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
    
    def test_logger_no_remove(self):
        new_log_file = f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log'
        order_book = OrderBook(new_log_file)
        order_book.add_order(self.create_bid(100, 5), random_str())
        order_book.add_order(self.create_ask(90, 7), random_str())
        with open(new_log_file, 'r') as f:
            lines = f.readlines()
            # the data in the now created log file is expected to match the following regex expressions
            regex = [
                r'BID \| timestamp: \d{10}\.\d{5,7}, side: b, price: 100, size: 5, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                r'ASK \| timestamp: \d{10}\.\d{5,7}, side: a, price: 90, size: 7, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                r'TRADE \| timestamp: \d{10}\.\d{5,7}, price: 100, size: 5, buyer_id: "[a-zA-Z0-9]{8}", seller_id: "[a-zA-Z0-9]{8}"',
                r'\t--> ASK id: \d{15} now has size: 2',
                r'\t--> BID id: \d{15} now has been exhausted',
                ]
            for i, line in enumerate(lines):
                self.assertRegex(line, regex[i])
    
    def test_logger_yes_remove(self):
        new_log_file = f'{TESTS_FOLDER_NAME}/{self._testMethodName}.log'
        order_book = OrderBook(new_log_file)
        bid = self.create_bid(100, 5)
        order_book.add_order(bid, random_str())
        ask = self.create_ask(90, 7)
        order_book.add_order(ask, random_str())
        with self.assertRaises(KeyError) as e:
            order_book.remove_order(bid.id, bid.sender_id)
            err_regex = r'^Tried to remove order but no such order exists\.\\nOrder id: \d{15}\. Order key: \(100, 5\)$'
            self.assertRegex(e.args[0], err_regex)
        
        order_book.remove_order(ask.id, ask.sender_id)
        with open(new_log_file, 'r') as f:
            lines = f.readlines()
            # the data in the now created log file is expected to match the following regex expressions
            regex = list(map(re.compile, [
                r'BID \| timestamp: \d{10}\.\d{5,7}, side: b, price: 100, size: 5, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                r'ASK \| timestamp: \d{10}\.\d{5,7}, side: a, price: 90, size: 7, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"',
                r'TRADE \| timestamp: \d{10}\.\d{5,7}, price: 100, size: 5, buyer_id: "[a-zA-Z0-9]{8}", seller_id: "[a-zA-Z0-9]{8}"',
                r'\t--> ASK id: \d{15} now has size: 2',
                r'\t--> BID id: \d{15} now has been exhausted',
                r'ASK (rm) | timestamp: \d{10}\.\d{5,7}, side: a, price: 90, size: 2, id: \d{15}, sender_id: "[a-zA-Z0-9]{8}"'
                ]
                             ))
            for i, line in enumerate(lines):
                self.assertRegex(line, regex[i])


if __name__ == '__main__':
    unittest.main()
