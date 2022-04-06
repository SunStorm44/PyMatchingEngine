import unittest

from engine.matching_engine import MatchingEngine
from engine.src.client import Client
from engine.src.enums import Side, OrderType


class TestMarketOrder(unittest.TestCase):
    def test_MarketBuy(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.BUY, 30)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 1)
        
        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 20)
        self.assertTrue(best_ask.show_quantity == 20)
        self.assertTrue(best_ask.displayed_quantity == 50)

    def test_MarketSell(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 30)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 1)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.total_quantity == 20)
        self.assertTrue(best_bid.show_quantity == 20)
        self.assertTrue(best_bid.displayed_quantity == 50)

    def test_MarketSweep(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 10, 100.00)
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 5, 99.00)
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 20, 98.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.MARKET, Side.SELL, 30)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 3)

        best_bid = exchange.orderbooks['BTC'].best_bid()
        self.assertTrue(best_bid.total_quantity == 5)
        self.assertTrue(best_bid.show_quantity == 5)
        self.assertTrue(best_bid.displayed_quantity == 20)


if __name__ == '__main__':
    unittest.main()
