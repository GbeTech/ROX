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

from bintrees.abctree import _ABCTree

from util import get_now
import bintrees
import logging


class Subscriber:
    def __init__(self):
        pass


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
        self.timestamp = get_now()  # since epoch
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
        """Orders are compared firstly by price. In case of equal prices, sizes are compared.
        Two equal Orders must have the same price and size."""
        return self.price, self.size

    def is_exhausted(self):
        return not self.size

    def __repr__(self):
        return f'timestamp: {self.timestamp}, side: {self.side}, price: {self.price}, size: {self.size}, id: {self.id}, sender_id: "{self.sender_id}"'


class Trade:
    def __init__(self, bid: Order, ask: Order):
        self.timestamp = get_now()  # since epoch
        self.size = self._finalize(bid, ask)
        self.price = bid.price
        self.buyer_id = bid.sender_id
        self.seller_id = ask.sender_id

    def _key(self):
        """Trades are compared firstly by price. In case of equal prices, sizes are compared.
        Two equal Trades must have the same price and size."""
        return self.price, self.size

    @staticmethod
    def _finalize(bid: Order, ask: Order):
        """Finalizes the trade between passed bid and ask.
        In case any side is "exhausted" (runs out of size), its size property is set to None via Order.size property setter.
        Assumes passed bid and ask can be finally traded.
        Returns the final trade size.
        """
        smallest_size = min(bid.size, ask.size)
        trade_size = smallest_size
        bid.size -= smallest_size
        ask.size -= smallest_size

        return trade_size

    def __repr__(self):
        return f'timestamp: {self.timestamp}, price: {self.price}, size: {self.size}, buyer_id: "{self.buyer_id}", seller_id: "{self.seller_id}"'


class Logger:
    def __init__(self, filename):
        self.filename = filename
        logging.basicConfig(format='%(message)s',
                            filename=filename,
                            level=logging.INFO,
                            filemode='w')

    def log_bid(self, bid):
        logging.info(f'BID | {bid}')

    def log_ask(self, ask):
        logging.info(f'ASK | {ask}')

    def log_trade(self, trade, bid, ask):
        logging.info(f'TRADE | {trade}')
        if ask.is_exhausted():
            logging.info(f'\t--> ASK id: {ask.id} now has been exhausted')
        else:
            logging.info(f'\t--> ASK id: {ask.id} now has size: {ask.size}')
        if bid.is_exhausted():
            logging.info(f'\t--> BID id: {bid.id} now has been exhausted')
        else:
            logging.info(f'\t--> BID id: {bid.id} now has size: {bid.size}')


class OrderBook:

    def __init__(self, logfile_full_path='logs/orderbook.log'):
        self.bids: _ABCTree = bintrees.AVLTree()
        self.asks: _ABCTree = bintrees.AVLTree()
        self.trades: _ABCTree = bintrees.AVLTree()
        self.logger = Logger(logfile_full_path)

    # O(log(n))
    def show_top(self):
        """Returns the highest bid and lowest ask orders"""
        return self.bids.max_item(), self.asks.min_item()

    # O(n)
    def show_trades(self):
        """Returns the list of trades sorted by time"""
        return sorted(self.trades.values(), key=lambda trade: trade.timestamp)

    # O(n)
    def show_orderbook(self):
        """Prints the current state orderbook in a human readable format"""
        print("\nBids:")
        for i, bid in enumerate(self.bids.values()):
            print(f'({i}) {bid}')

        print("\nAsks:")
        for i, ask in enumerate(self.asks.values()):
            print(f'({i}) {ask}')

    # called by add_order, when a trade has occurred, notify subscribers of the trade
    def notify_trade(self, trade_event: Trade, subscribers: [Subscriber]):
        return

    # Add an order, notify if a trade has occurred
    # record the order (and trade) in a log
    # O(log(n))
    def add_order(self, order: Order, sender_id):
        """
        Logs the order to log file.
        Adds the order to its suitable tree (bids or asks).
        Tries to finalize a trade or multiple trades between the order and existing bids / asks.
        If a bid, ask, or both are exhausted during the process (i.e. ran out of "size"),
        they are deleted from their respective trees.
        Calls self._add_ask if order.side is Order.ASK, otherwise calls self._add_bid
        """
        order.sender_id = sender_id
        if order.side == Order.BID:
            self._add_bid(order)

        else:
            self._add_ask(order)

    # O(log(n))
    def _add_ask(self, ask: Order):
        self.logger.log_ask(ask)
        ask_key = ask._key()
        self.asks.insert(ask_key, ask)
        should_continue = True
        while should_continue:
            # Keep trying to finalize trades with current order (ask)
            # Stop when no matching bid was found, or when ask is exhausted (i.e. sell order fully satisfied)
            trade = self._try_sell(ask)
            if trade:
                # Found someone who's willing to buy high enough
                self.trades.insert(trade._key(), trade)
                if ask.is_exhausted():
                    # The order was fully sold
                    # Remove it from tree
                    self.asks.pop(ask_key)
                    should_continue = False
            else:
                should_continue = False

    # O(log(n))
    def _add_bid(self, bid: Order):
        self.logger.log_bid(bid)
        bid_key = bid._key()
        self.bids.insert(bid_key, bid)
        should_continue = True
        while should_continue:
            # Keep trying to finalize trades with current order (bid)
            # Stop when no matching ask was found, or when bid is exhausted (i.e. buy order fully satisfied)
            trade = self._try_buy(bid)
            if trade:
                # Found someone who's willing to sell low enough
                self.trades.insert(trade._key(), trade)

                if bid.is_exhausted():
                    # The order was fully bought
                    # Remove it from tree
                    self.bids.pop(bid_key)
                    should_continue = False
            else:
                should_continue = False

    # remove an order
    # record the removal order in the log
    def remove_order(self, order_id, sender_id):
        return

    # def make_trade(self, order):
    #     # print(f'OrderBook.make_trade(order = {order.id})')
    #     if order.side == Order.BID:
    #         return self._try_buy(order)
    #
    #     else:  # order is an ASK
    #         return self._try_sell(order)
    # O(log(n))
    def _try_buy(self, bid: Order) -> Trade or None:
        """
        Finalizes a trade between the passed bid and the lowest ask order in orderbook,
        given passed bid is higher or equal to the lowest ask.
        Returns a Trade if one was finalized, otherwise returns None.
        """
        try:
            ask_key, lowest_ask = self.asks.min_item()
        except ValueError:  # self.asks is empty
            return None

        trade = None
        if lowest_ask <= bid:  # someone offered a low-enough sell price and a trade will be made
            trade = Trade(bid, lowest_ask)
            self.logger.log_trade(trade, bid, lowest_ask)
            trade_subscribers = bid.subscribers.extend(lowest_ask.subscribers)
            self.notify_trade(trade, trade_subscribers)
            if lowest_ask.is_exhausted():
                self.asks.pop(ask_key)

        return trade

    # O(log(n))
    def _try_sell(self, ask: Order) -> Trade or None:
        """
        Finalizes a trade between the passed ask and the highest bid order in orderbook,
        given passed ask is lower or equal to the highest bid.
        Returns a Trade if one was finalized, otherwise returns None.
        """
        try:
            bid_key, highest_bid = self.bids.max_item()
        except ValueError:  # self.bids is empty
            return None

        trade = None
        if highest_bid >= ask:  # someone bid high enough and a trade will be made
            trade = Trade(highest_bid, ask)
            self.logger.log_trade(trade, highest_bid, ask)
            if highest_bid.is_exhausted():
                self.bids.pop(bid_key)

        return trade