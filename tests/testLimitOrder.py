import unittest

from engine.matching_engine import MatchingEngine
from engine.src.client import Client
from engine.src.enums import Side, OrderType


class TestLimitOrder(unittest.TestCase):
    def test_NewBidOrder(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 99.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        bids, asks = exchange.orderbooks['BTC'].get_client_orders(client_1.client_id)
        self.assertTrue(bids[-1].instrument == 'BTC')
        self.assertTrue(bids[-1].order_type == OrderType.LIMIT)
        self.assertTrue(bids[-1].price == 99.00)
        self.assertTrue(bids[-1].total_quantity == 10)
        self.assertTrue(bids[-1].displayed_quantity == 10)
        self.assertTrue(bids[-1].show_quantity == 10)

    def test_NewAskOrder(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 99.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 0)

        bids, asks = exchange.orderbooks['BTC'].get_client_orders(client_1.client_id)
        self.assertTrue(asks[-1].instrument == 'BTC')
        self.assertTrue(asks[-1].order_type == OrderType.LIMIT)
        self.assertTrue(asks[-1].price == 99.00)
        self.assertTrue(asks[-1].total_quantity == 10)
        self.assertTrue(asks[-1].displayed_quantity == 10)
        self.assertTrue(asks[-1].show_quantity == 10)

    def test_OrderQueue_1(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 99.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 30, 100.00)

        self.assertTrue(exchange.orderbooks['BTC'].best_bid_price() == 100.00)

    def test_OrderQueue_2(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 99.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 30, 99.00)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.client_id == client_1.client_id)

    def test_level_size(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 99.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 30, 99.00)

        lot_num = exchange.orderbooks['BTC'].get_level_quantity(side=Side.BUY, price=99.00)
        self.assertTrue(lot_num == 40)

    def test_full_trade(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 1)

        trade = exchange.trades[-1]
        self.assertTrue(trade.price == 100)
        self.assertTrue(trade.quantity == 10)

    def test_partial_trade(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 5, 100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 1)

        trade = exchange.trades[-1]
        self.assertTrue(trade.price == 100)
        self.assertTrue(trade.quantity == 5)

        order = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(order.client_id == client_1.client_id)
        self.assertTrue(order.total_quantity == 5)
        self.assertTrue(order.show_quantity == 5)


if __name__ == '__main__':
    unittest.main()
