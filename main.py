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
# when a trade occurs, the subscribers (traders) need to be notified of the trade, and the trade should be logged

# order sides
BID = "b"
ASK = "a"


class Trade:
    def __init__(self):
        self.time: int  # seconds since epoch
        self.size: int
        self.price: int
        self.buyer_id: str
        self.seller_id: str


class Order:
    def __init__(self):
        self.time: int  # seconds since epoch
        self.side: str  # "b" (bid) or "a" (ask)
        self.size: int
        self.price: int
        self.id: int
        self.name: str


class OrderBook:

    def __init__(self):
        self.bids = {}
        self.asks = {}
        # feel free to add more members as required

    # Returns the highest bid and lowest ask orders
    def show_top(self):
        # please implement
        best_bid = 0
        best_ask = 0
        return best_bid, best_ask

    # Returns the list of trades sorted by time
    def show_trades(self):
        # please implement
        return

    # print the current state orderbook in a human readable format
    def show_orderbook(self):
        # please implement
        return

    # called by add_order, when a trade has occurred, notify subscribers of the trade
    def notify_trade(self, trade_event, subscribers):
        # please implement as required
        return

        # Add an order, notify if a trade has occurred

    # record the order (and trade) in a log
    def add_order(self, order, sender_id):
        # please implement
        return

        # remove an order

    # record the removal order in the log
    def remove_order(self, orderId, sender_id):
        # please implement
        return