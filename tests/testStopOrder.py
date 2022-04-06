import unittest

from engine.matching_engine import MatchingEngine
from engine.src.client import Client
from engine.src.enums import Side, OrderType


class TestStopOrder(unittest.TestCase):
    def test_StopLimitBid(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 102.00, stop_flag=True, trigger_price=100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        self.assertTrue(len(exchange.stop_bids) == 1)
        self.assertTrue(len(exchange.stop_asks) == 0)
        stop_bid = exchange.stop_bids['BTC']
        self.assertTrue(stop_bid[0].order_type == OrderType.LIMIT)

    def test_StopLimitAsk(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 102.00, stop_flag=True, trigger_price=100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        self.assertTrue(len(exchange.stop_bids) == 0)
        self.assertTrue(len(exchange.stop_asks) == 1)
        stop_ask = exchange.stop_asks['BTC']
        self.assertTrue(stop_ask[0].order_type == OrderType.LIMIT)

    def test_StopMarketBid(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 50, stop_flag=True, trigger_price=100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        self.assertTrue(len(exchange.stop_bids) == 1)
        self.assertTrue(len(exchange.stop_asks) == 0)
        stop_bid = exchange.stop_bids['BTC']
        self.assertTrue(stop_bid[0].order_type == OrderType.MARKET)

    def test_StopMarketAsk(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 50, stop_flag=True, trigger_price=100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        self.assertTrue(len(exchange.stop_bids) == 0)
        self.assertTrue(len(exchange.stop_asks) == 1)
        stop_ask = exchange.stop_asks['BTC']
        self.assertTrue(stop_ask[0].order_type == OrderType.MARKET)

    def test_StopQueue(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 102.00, stop_flag=True, trigger_price=100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 101.00, stop_flag=True, trigger_price=101.00)
        stop_bid = exchange.stop_bids['BTC']
        self.assertTrue(stop_bid[0].client_id == client_1.client_id)

    def test_StopTriggered_1(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00, stop_flag=True, trigger_price=101.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 101.00)

        client_3 = Client(client_name='Clark Kent')
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 5, 101.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 2)

        self.assertTrue(len(exchange.stop_bids) == 0)
        self.assertTrue(len(exchange.stop_asks['BTC']) == 0)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 45)
        self.assertTrue(best_ask.price == 100.00)

    def test_stopTriggered_2(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 50, stop_flag=True, trigger_price=101.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 101.00)

        client_3 = Client(client_name='Clark Kent')
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 5, 101.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 2)

        self.assertTrue(len(exchange.stop_bids['BTC']) == 0)
        self.assertTrue(len(exchange.stop_asks) == 0)

    def test_MultipleStopsTriggered_1(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 50, stop_flag=True, trigger_price=100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 10, stop_flag=True, trigger_price=101.00)
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 15, stop_flag=True, trigger_price=102.00)

        client_3 = Client(client_name='Clark Kent')
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 100.00)
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 200, 101.00)

        client_4 = Client(client_name='Adam Brown')
        client_4.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 12)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 4)

        self.assertTrue(len(exchange.stop_bids['BTC']) == 1)
        self.assertTrue(len(exchange.stop_asks) == 0)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 138)
        self.assertTrue(best_ask.price == 101.00)

    def test_MultipleStopsTriggered_2(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 50, stop_flag=True, trigger_price=100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 10, stop_flag=True, trigger_price=99.00)
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 15, stop_flag=True, trigger_price=98.00)

        client_3 = Client(client_name='Clark Kent')
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 100.00)
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 200, 99.00)

        client_4 = Client(client_name='Adam Brown')
        client_4.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 10)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 3)

        self.assertTrue(len(exchange.stop_bids) == 0)
        self.assertTrue(len(exchange.stop_asks['BTC']) == 1)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.total_quantity == 140)
        self.assertTrue(best_bid.price == 99.00)


if __name__ == '__main__':
    unittest.main()
