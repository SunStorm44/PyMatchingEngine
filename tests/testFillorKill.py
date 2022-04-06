import unittest

from engine.matching_engine import MatchingEngine
from engine.src.client import Client
from engine.src.enums import Side, OrderType


class TestFillOrKill(unittest.TestCase):
    def test_MarketKill(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00)
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 101.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 75, fok_flag=True)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 2)
        self.assertTrue(len(exchange.trades) == 0)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 50)

    def test_LimitKill(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 75, 99.00, fok_flag=True)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.total_quantity == 50)

    def test_MarketFill(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 100.00)

        client_2 = Client(client_name='Stacey White')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 30, 100.00)

        client_3 = Client(client_name='Jack Jones')
        client_3.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 75, fok_flag=True)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 2)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.total_quantity == 5)

    def test_LimitFill(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00)

        client_2 = Client(client_name='Stacey White')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 30, 101.00)
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 10, 102.00)

        client_3 = Client(client_name='Jack Jones')
        client_3.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 75, 101.00, fok_flag=True)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 2)
        self.assertTrue(len(exchange.trades) == 2)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 5)


if __name__ == '__main__':
    unittest.main()
