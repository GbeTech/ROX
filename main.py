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
from typing import Dict, Any

from bintrees.abctree import _ABCTree

from util import get_now
import bintrees
import logging


class Logger:
    def __init__(self, filename):
        self.filename = filename
        logging.basicConfig(format='%(message)s',
                            filename=filename,
                            level=logging.INFO,
                            filemode='w')

    def log_bid(self, bid, removed=False):
        if removed:
            logging.info(f'BID (rm) | {bid}')
        else:
            logging.info(f'BID | {bid}')

    def log_ask(self, ask, removed=False):
        if removed:
            logging.info(f'ASK (rm) | {ask}')
        else:
            logging.info(f'ASK | {ask}')

    def log_trade(self, trade):
        logging.info(f'TRADE | {trade}')
        if trade.ask.is_exhausted():
            logging.info(f'\t--> ASK id: {trade.ask.id} now has been exhausted')
        else:
            logging.info(f'\t--> ASK id: {trade.ask.id} now has size: {trade.ask.size}')
        if trade.bid.is_exhausted():
            logging.info(f'\t--> BID id: {trade.bid.id} now has been exhausted')
        else:
            logging.info(f'\t--> BID id: {trade.bid.id} now has size: {trade.bid.size}')


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
        """An exhausted order is one that met all its requirements until 'size' is None."""
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

        # The actual bid and ask objects are used when
        # logging a trade (order.id and order.size are needed)
        # and when notifying subscribers
        self.bid = bid
        self.ask = ask

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

    def total_value(self):
        return self.price * self.size

    def bid_ask_difference(self):
        return self.price - self.ask.price

    def __repr__(self):
        return f'timestamp: {self.timestamp}, price: {self.price}, size: {self.size}, buyer_id: "{self.buyer_id}", seller_id: "{self.seller_id}"'


class Subscriber:

    def __init__(self, sender_id):
        self.id = sender_id
        self.email = f"{self.id}@example.com"

        # Values are not removed or changed in self.orders_ids, regardless or the state of the order.
        self.orders_ids = []

    def is_subscribed_to_any(self, *orders):
        """Returns True if subscribed to any of the passed orders"""
        for order in orders:
            if order.id in self.orders_ids:
                return True
        return False

    def notify(self, trade: Trade):
        """Notifies the subscriber of a trade event relating to one her of orders.
        Sends an email to her address, specifying the trade's details, total expense/income, and the status of the order."""
        return
        import time

        if trade.buyer_id == self.id:
            # Subscriber is on the buyer's side
            msg = self._generate_bidder_msg(trade)
        else:
            # Subscriber is on the sellers's side
            msg = self._generate_asker_msg(trade)

        _connect = lambda port: print(f'\n***Server connected to port: {port}')
        _sendmail = lambda address, text: (print(f'\nSending email to {address}:\n\t{text}'),
                                           time.sleep(1),
                                           print('\nEmail sent successfully'))
        _quit = lambda: print('\nServer closed***')

        mock_server = {'connect':  _connect,
                       'sendmail': _sendmail,
                       'quit':     _quit, }

        mock_server['connect'](25)
        mock_server['sendmail'](self.email, msg)
        mock_server['quit']()

    def _generate_asker_msg(self, trade):
        trade_total_value = trade.total_value()
        bid_ask_difference = trade.bid_ask_difference()
        msg = f'''
            A trade has been completed with your ask order, id: {trade.ask.id}.
            {trade.size} units have been sold at {trade.price}$ each. 
            Total income: {trade_total_value}$.'''
        if bid_ask_difference:
            msg += f'''
            This is {bid_ask_difference} additional dollars a unit, compared to your original sell offer (at {trade.ask.price}$),
            which translate to {bid_ask_difference*trade.size}$ above what you have originally planned.  
            '''
        if trade.ask.is_exhausted():
            msg += 'Your ask requirements were fully satisfied.'
        else:
            msg += f'Your ask was not exhausted: {trade.ask.size} units left to sell.'
        return msg

    def _generate_bidder_msg(self, trade):
        msg = f'''
            A trade has been completed with your bid order, id: {trade.bid.id}.
            {trade.size} units have been bought at {trade.price}$ each.
            Total expenses: {trade.total_value()}$. 
            '''
        if trade.bid.is_exhausted():
            msg += 'Your bid requirements were fully satisfied.'
        else:
            msg += f'Your bid was not exhausted: {trade.bid.size } units left to buy.'
        return msg


class OrderBook:

    def __init__(self, logfile_full_path='logs/orderbook.log'):
        self.bids: _ABCTree = bintrees.AVLTree()
        self.asks: _ABCTree = bintrees.AVLTree()

        # This is to retrieve an order *by order_id* from the trees in O(log(n)). (self.remove_order())
        # self.bids and self.asks are indexed by Order._key(), which is (self.price, self.size).
        self.order_id_key_translate = {}
        self.trades = {}
        self.subscribers: Dict[str, Subscriber] = {}
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
        if self.bids.is_empty():
            print('-- No bids --')
        else:
            for i, bid in enumerate(self.bids.values()):
                print(f'({i}) {bid}')

        print("\nAsks:")
        if self.asks.is_empty():
            print('-- No asks --')
        else:
            for i, ask in enumerate(self.asks.values()):
                print(f'({i}) {ask}')

    def notify_trade(self, trade, subscribers):
        """Notifies each of the passed subscribers of the trade event."""
        for subscriber in subscribers:
            subscriber.notify(trade)

    # O(log(n))
    def add_order(self, order: Order, sender_id):
        """
        Indexes passed order by order.id in self.order_id_key_translate, for O(log(n)) retrieval in self.remove_order().
        Updates the subscriptions list of the sender to include the current order id (creates a new Subscriber if needed).
        Calls self._add_ask if order.side is Order.ASK, otherwise calls self._add_bid
        Logs the order to log file.
        Inserts the order to its suitable tree (bids or asks).
        Tries to finalize a trade or multiple trades between the order and existing bids / asks, until the order is exhausted or no trade could be done.
        Logs the trade to log file and notifies all its subscriptors via email.
        If a bid, ask, or both are exhausted during the process (i.e. ran out of "size"),
        they are deleted from their respective trees.
        """
        order.sender_id = sender_id
        self.order_id_key_translate[order.id] = order._key()

        # Add order to subscriber's orders. Create new subscriber if none was found
        subscriber: Subscriber = self.subscribers.get(sender_id)
        if subscriber:
            subscriber.orders_ids.append(order.id)
        else:
            subscriber = Subscriber(sender_id)
            subscriber.orders_ids.append(order.id)
            self.subscribers[sender_id] = subscriber

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
                self.trades[trade._key()] = trade
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
                self.trades[trade._key()] = trade
                if bid.is_exhausted():
                    # The order was fully bought
                    # Remove it from tree
                    self.bids.pop(bid_key)
                    should_continue = False
            else:
                should_continue = False

    def remove_order(self, order_id, sender_id):
        """
        Removes an order from its respective tree.
        Records the removal in the log.
        """
        order_key = self.order_id_key_translate[order_id]
        bid_to_remove = self.bids.get(order_key)
        if bid_to_remove:
            if bid_to_remove.sender_id == sender_id:
                self.logger.log_bid(bid_to_remove, removed=True)
                self.bids.remove(order_key)

        else:  # order is not a bid
            ask_to_remove = self.asks.get(order_key)
            if not ask_to_remove:
                raise KeyError(f'''Tried to remove order but no such order exists.
                Order id: {order_id}. Order key: {order_key}''')

            if ask_to_remove.sender_id == sender_id:
                self.logger.log_ask(ask_to_remove, removed=True)
                self.asks.remove(order_key)

    def _subscribers_of_orders(self, *orders):
        """Returns a list of Subscribers that have subscribed to any of the passed orders"""
        return [sub for sub in self.subscribers.values()
                if sub.is_subscribed_to_any(*orders)]

    # O(log(n))
    def _try_buy(self, bid: Order) -> Trade or None:
        """
        Finalizes a trade between the passed bid and the lowest ask order in orderbook,
        given passed bid is higher or equal to the lowest ask.
        If a trade was finalized, logs the trade to the log and notifies all of its subscribers.
        If a trade was not finalized, returns None.
        """
        if self.asks.is_empty():
            return None

        ask_key, lowest_ask = self.asks.min_item()

        trade = None
        if lowest_ask <= bid:  # someone offered a low-enough sell price and a trade will be made
            trade = Trade(bid, lowest_ask)

            # log trade
            self.logger.log_trade(trade)

            # get all who subscribed to either side
            trade_subscribers = self._subscribers_of_orders(bid, lowest_ask)

            # notify them about the trade
            self.notify_trade(trade, trade_subscribers)

            if lowest_ask.is_exhausted():
                self.asks.pop(ask_key)

        return trade

    # O(log(n))
    def _try_sell(self, ask: Order) -> Trade or None:
        """
        Finalizes a trade between the passed ask and the highest bid order in orderbook,
        given passed ask is lower or equal to the highest bid.
        If a trade was finalized, logs the trade to the log and notifies all of its subscribers.
        If a trade was not finalized, returns None.
        """
        if self.bids.is_empty():
            return None

        bid_key, highest_bid = self.bids.max_item()
        trade = None
        if highest_bid >= ask:  # someone bid high enough and a trade will be made
            trade = Trade(highest_bid, ask)
            self.logger.log_trade(trade)

            # get all who subscribed to either side
            trade_subscribers = self._subscribers_of_orders(highest_bid, ask)

            # notify them about the trade
            self.notify_trade(trade, trade_subscribers)

            if highest_bid.is_exhausted():
                self.bids.pop(bid_key)

        return trade