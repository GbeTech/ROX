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
        This happens when set to 0, negative number or or any "illegal" value (None, False, empty str etc)"""
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
        return f'timestamp: {self.timestamp}, side: {self.side}, price: {self.price}, size: {self.size}, id: {self.id}, sender_id: {self.sender_id}'


class Trade:
    def __init__(self, bid: Order, ask: Order):
        print(f'''Trade.__init__(bid = 
        {bid}, 
        ask = 
        {ask})''')
        self.timestamp = get_now()  # seconds since epoch
        self.size = self._finalize(bid, ask)
        self.price = bid.price
        self.buyer_id = bid.sender_id
        self.seller_id = ask.sender_id

        print(f'''
        Trade was made.
        seller:
        {ask}
        buyer:
        {bid} 
        ''')

    @staticmethod
    def _finalize(bid, ask):
        """Finalizes the trade.
        In case any side is "exhausted" (runs out of size), its size property is set to None.
        Returns the final trade size."""
        smallest_size = min(bid.size, ask.size)
        trade_size = smallest_size
        bid.size -= smallest_size
        ask.size -= smallest_size

        # Seller has enough units to satisfy buyer's demands. Bid is "nullified".
        # if ask.size - bid.size >= 0:
        #     trade_size = bid.size
        #     ask.size -= bid.size
        #     bid.size = None
        #
        # # Seller does NOT have enough units to satisfy buyer's demands. Ask is "nullified".
        # else:
        #     trade_size = ask.size
        #     bid.size -= ask.size
        #     ask.size = None

        return trade_size

    def __repr__(self):
        return self.print_data()

    def print_data(self):
        return f'timestamp: {self.timestamp}, price: {self.price}, size: {self.size}, buyer_id: {self.buyer_id}, seller_id: {self.seller_id}'


class OrderBook:

    def __init__(self, log_file_name):
        self.bids: _ABCTree = bintrees.AVLTree()
        self.asks: _ABCTree = bintrees.AVLTree()
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
        return

    # called by add_order, when a trade has occurred, notify subscribers of the trade
    def notify_trade(self, trade_event, subscribers):
        return

    # Add an order, notify if a trade has occurred
    # record the order (and trade) in a log
    def add_order(self, order, sender_id):
        """
        :param order: The order to add
        :type order: Order
        :param sender_id: The id of the person who did the order
        :type sender_id: str
        :return:
        :rtype:
        """
        order.sender_id = sender_id
        trades = []
        order_key = order._key()
        if order.side == Order.BID:
            self.bids.insert(order_key, order)
            while True:
                trade = self._try_buy(order)
                if not trade:
                    break
                trades.append(trade)
                if order.is_exhausted():
                    self.bids.pop(order_key)
                    break

        else:
            self.asks.insert(order_key, order)
            while True:
                trade = self._try_sell(order)
                if not trade:
                    break
                trades.append(trade)
                if order.is_exhausted():
                    self.asks.pop(order_key)
                    break

        # trade = self.make_trade(order)
        # if trade:
        #     breakpoint()

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

    def _try_buy(self, bid: Order):
        try:
            ask_key, lowest_ask = self.asks.min_item()
        except ValueError:  # self.asks is empty: no asks to match passed bid
            return

        if lowest_ask < bid:
            trade = Trade(bid, lowest_ask)
            if lowest_ask.is_exhausted():
                self.asks.pop(ask_key)
            return trade
        else:
            pass
            for order_id, _bid in self.bids.items():
                pass

    def _try_sell(self, ask: Order):
        try:
            bid_key, highest_bid = self.bids.max_item()
        except ValueError:  # self.bids is empty: no bids to match passed ask
            return

        if highest_bid > ask:  # someone bid high enough and is willing to buy
            trade = Trade(highest_bid, ask)
            if highest_bid.is_exhausted():
                self.bids.pop(bid_key)
            return trade
        else:
            pass
            for order_id, _ask in self.asks.items():
                pass


order_book = OrderBook('test_log.log')
order_0 = Order(side=Order.BID, price=100, size=10)
order_1 = Order(Order.BID, 70, 15)
order_book.add_order(order_0, sender_id=random_str())
order_book.add_order(order_1, random_str())

order_book.add_order(Order(Order.ASK, 99, 8), random_str())
order_book.add_order(Order(Order.ASK, 98, 2), random_str())
breakpoint()