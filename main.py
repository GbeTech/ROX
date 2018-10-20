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
from util import get_now, random_str
import tree
# order sides
BID = "b"
ASK = "a"


class Order:
    def __gt__(self, other):
        return self.price > other.price

    def __lt__(self, other):
        return self.price < other.price

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
        self.side = side  # "b" (bid) or "a" (ask)
        self.size = size
        self.price = price
        self.id = id(self)
        self.sender_id = ''

    def is_finalized(self):
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

        # Seller has enough units to satisfy buyer's demands. Bid is "nullified".
        if ask.size - bid.size >= 0:
            self.size = bid.size
            ask.size -= bid.size
            bid.size = 0

        # Seller does NOT have enough units to satisfy buyer's demands. Ask is "nullified".
        else:
            self.size = ask.size
            bid.size -= ask.size
            ask.size = 0

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

    def __repr__(self):
        return self.print_data()

    def print_data(self):
        return f'timestamp: {self.timestamp}, price: {self.price}, size: {self.size}, buyer_id: {self.buyer_id}, seller_id: {self.seller_id}'


class OrderBook:

    def __init__(self, log_file_name):
        self.bids = OrderedDict()
        self.asks = OrderedDict()
        self.log_file_name = log_file_name
        self.highest_bid: Order = None
        self.lowest_ask: Order = None
        # feel free to add more members as required

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
        # print(f'OrderBook.add_order(order = {order.id}, sender_id = {sender_id})')
        order.sender_id = sender_id
        if order.side == BID:
            self.bids[order.id] = order
            if not self.highest_bid or self.highest_bid < order:
                self.highest_bid = order

        else:
            self.asks[order.id] = order
            if not self.lowest_ask or self.lowest_ask > order:
                self.lowest_ask = order

        trade = self.make_trade(order)
        # if trade:
        #     breakpoint()

        # with open(os.path.join('logs', self.log_file_name), 'a') as log:
        #     log.writelines([order.print_data(), '\n'])

    # remove an order
    # record the removal order in the log
    def remove_order(self, orderId, sender_id):
        return

    def make_trade(self, order):
        # print(f'OrderBook.make_trade(order = {order.id})')
        if order.side == BID:
            return self._finalize_buy(order)

        else:  # order is an ASK
            return self._finalize_sell(order)

    def _finalize_buy(self, bid: Order):
        # print(f'OrderBook._finalize_buy(bid = {bid.id})')
        if not self.lowest_ask:
            return None
        if self.lowest_ask < bid:
            trade = Trade(bid, self.lowest_ask)
            return trade
        else:
            pass
            for order_id, _bid in self.bids.items():
                pass

    def _finalize_sell(self, ask: Order):
        # print(f'OrderBook._finalize_sell(ask = {ask.id})')
        if not self.highest_bid:
            return None
        if self.highest_bid > ask:
            trade = Trade(self.highest_bid, ask)
            if self.highest_bid.is_finalized():
                self.bids.pop(self.highest_bid.sender_id)
            return trade
        else:
            pass
            for order_id, _ask in self.asks.items():
                pass


order_book = OrderBook('test_log.log')
order_0 = Order(side=BID, price=100, size=10)
order_1 = Order(BID, 70, 15)
order_book.add_order(order_0, sender_id=random_str())
order_book.add_order(order_1, random_str())

order_book.add_order(Order(ASK, 99, 8), random_str())
order_book.add_order(Order(ASK, 98, 2), random_str())