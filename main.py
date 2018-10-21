# implement an orderbook,
# and a test which creates orders, sends them to the book,
# and prints the resulting state of the orderbook/trades.

# 1.Implement an order book class: here is a sample python API,
# and a unit test to add bids, asks, show the orderbook afterwards,
# and show the trades


# The orderbook contains bid orders and ask orders,
# Each order has the following members:
#   Time: the time at which the order was sent
#   Side: Bid/Ask - bid means buy, and ask means sell
#   Size: the amount to trade
#   Price: the price at which to trade
#   OrderId: a unique tracking number for the order
#   Name: the name/Id of the person doing the order
# A trade occurs when an order was entered that intersects an existing order,
# Each Trade has the following members:
#   Time
#   Price
#   Size
#   BuyerId
#   SellerId
# for example:
# if the orderbook contains a bid order at price=100, size=10
# and we just receive an ask order at price=99, size = 12
# a trade will happen at price 100, for size 10,
# and the orderbook will now contain an ask order with price=99, size=2
# when a trade occurs, the subscribers (traders) need to be notified of the trade,
# and the trade should be logged
import os
from collections import OrderedDict

from bintrees.abctree import _ABCTree

from util import get_now, random_str
import bintrees


class Order:
    # order sides
    BID = "b"
    ASK = "a"

    def __gt__(self, other):
        return self._key() > other._key()

    def __lt__(self, other):
        return self._key() < other._key()

    def __ge__(self, other):
        return self._key() >= other._key()

    def __le__(self, other):
        return self._key() <= other._key()

    def __eq__(self, other):
        return self._key() == other._key()

    def __init__(self, side, price, size):
        """
        :param side:
        :type side: str
        :param price:
        :type price: int
        :param size:
        :type size: int
        :param id:
        :type id: int
        """
        self.timestamp = get_now()  # seconds since epoch
        if side != self.BID and side != self.ASK:
            raise ValueError(f'''Tried to initialize Order instance with illegal order side arg: "{side}". 
                Only "{self.BID}" or "{self.ASK}" allowed.''')

        self.side = side  # "b" (bid) or "a" (ask)
        self._size = size
        self.price = price
        self.id = id(self)
        self.sender_id = ''

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        """Normalize Order.size property to None whenever size has been "exhausted".
        This happens when size is set to 0, negative number or or any "illegal" value (None, False, empty str etc)"""
        if not value or value < 0:
            self._size = None
        else:
            self._size = value

    def _key(self):
        return self.price, self.size, self.timestamp

    def is_exhausted(self):
        return not self.size

    def __repr__(self):
        return self.print_data()

    def print_data(self):
        return f'timestamp: {self.timestamp}, side: {self.side}, price: {self.price}, size: {self.size}, id: {self.id}, sender_id: "{self.sender_id}"'


class Trade:
    def __init__(self, bid: Order, ask: Order):
        self.timestamp = get_now()  # seconds since epoch
        self.size = self._finalize(bid, ask)
        self.price = bid.price
        self.buyer_id = bid.sender_id
        self.seller_id = ask.sender_id

    @staticmethod
    def _finalize(bid, ask):
        """Finalizes the trade.
        In case any side is "exhausted" (runs out of size), its size property is set to None via size property setter.
        Returns the final trade size."""
        smallest_size = min(bid.size, ask.size)
        trade_size = smallest_size
        bid.size -= smallest_size
        ask.size -= smallest_size

        return trade_size

    def _key(self):
        return self.price, self.size, self.timestamp

    def __repr__(self):
        return self.print_data()

    def print_data(self):
        return f'timestamp: {self.timestamp}, price: {self.price}, size: {self.size}, buyer_id: "{self.buyer_id}", seller_id: "{self.seller_id}"'


class OrderBook:

    def __init__(self, log_file_name='test_log.log'):
        self.bids: _ABCTree = bintrees.AVLTree()
        self.asks: _ABCTree = bintrees.AVLTree()
        self.trades: _ABCTree = bintrees.AVLTree()
        self.log_file_name = log_file_name

    # Returns the highest bid and lowest ask orders
    def show_top(self):
        best_bid = 0
        best_ask = 0
        return best_bid, best_ask

    # Returns the list of trades sorted by time
    def show_trades(self):
        return

    # print the current state orderbook in a human readable format
    def show_orderbook(self):
        self.pprint()

    # called by add_order, when a trade has occurred, notify subscribers of the trade
    def notify_trade(self, trade_event, subscribers):
        return

    # Add an order, notify if a trade has occurred
    # record the order (and trade) in a log
    def add_order(self, order: Order, sender_id):
        """
        Adds an order to its suitable tree (bids or asks).
        Tries to finalize a trade or multiple trades between the order and existing bids / asks.
        If a bid, ask, or both are exhausted during the process (i.e. ran out of "size"), they are deleted from their respective trees.
        Returns a list of Trade if any were finalized, otherwise an empty list.
        """
        order.sender_id = sender_id
        # trades = []
        order_key = order._key()
        if order.side == Order.BID:
            self.bids.insert(order_key, order)
            while True:
                trade = self._try_buy(order)
                if not trade:
                    break
                self.trades.insert(trade._key(), trade)
                if order.is_exhausted():
                    self.bids.pop(order_key)
                    break

        else:
            self.asks.insert(order_key, order)
            while True:
                trade = self._try_sell(order)
                if not trade:
                    break
                self.trades.insert(trade._key(), trade)
                if order.is_exhausted():
                    self.asks.pop(order_key)
                    break

        # with open(os.path.join('logs', self.log_file_name), 'a') as log:
        #     log.writelines([order.print_data(), '\n'])

    # remove an order
    # record the removal order in the log
    def remove_order(self, orderId, sender_id):
        return

    # def make_trade(self, order):
    #     # print(f'OrderBook.make_trade(order = {order.id})')
    #     if order.side == Order.BID:
    #         return self._try_buy(order)
    #
    #     else:  # order is an ASK
    #         return self._try_sell(order)

    def _try_buy(self, bid: Order) -> Trade or None:
        """
        Finalizes a trade between the passed bid and the lowest ask order, if passed bid is higher or equal to the lowest ask.
        Tries to finalize more trades until bid is exhausted.
        Returns a list of Trade or an empty list of none was finalized.
        """
        trade = None
        try:
            ask_key, lowest_ask = self.asks.min_item()
        except ValueError:  # self.asks is empty: no asks to match passed bid
            return trade

        if lowest_ask <= bid:  # someone offered a low-enough sell price and a trade will be made
            trade = Trade(bid, lowest_ask)
            if lowest_ask.is_exhausted():
                self.asks.pop(ask_key)

        return trade

    def _try_sell(self, ask: Order) -> Trade or None:
        """
        Finalizes a trade between the passed ask and the highest bid order, if passed ask is lower or equal to the highest bid.
        Tries to finalize more trades until bid is exhausted.
        Returns a list of Trade or an empty list of none was finalized.
        """
        trade = None
        try:
            bid_key, highest_bid = self.bids.max_item()
        except ValueError:  # self.bids is empty: no bids to match passed ask
            return trade

        if highest_bid >= ask:  # someone bid high enough and a trade will be made
            trade = Trade(highest_bid, ask)
            if highest_bid.is_exhausted():
                self.bids.pop(bid_key)

        return trade

    def pprint(self):
        print("\nBids:")
        for bid in self.bids.values():
            print(bid)

        print("Asks:")
        for ask in self.asks.values():
            print(ask)


"""order_book = OrderBook()
order_0 = Order(side=Order.BID, price=100, size=10)
order_1 = Order(Order.BID, 70, 15)
order_book.add_order(order_0, sender_id=random_str())
order_book.add_order(order_1, random_str())

order_book.add_order(Order(Order.ASK, 99, 8), random_str())
order_book.pprint()
order_book.add_order(Order(Order.ASK, 98, 3), random_str())

order_book.pprint()

order_book.add_order(Order(Order.ASK, 65, 20), random_str())

order_book.pprint()

order_book.add_order(Order(Order.BID, 99, 7), random_str())

order_book.pprint()"""