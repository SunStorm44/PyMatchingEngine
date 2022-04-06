import unittest

from engine.matching_engine import MatchingEngine
from engine.src.client import Client
from engine.src.enums import Side, OrderType


class TestIcebergOrder(unittest.TestCase):
    def test_PassiveIcebergBid(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 100.00, iceberg_flag=True,
                             displayed_quantity=10)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 0)

        best_bid = exchange.orderbooks['BTC'].best_bid()

        self.assertTrue(best_bid.total_quantity == 50)
        self.assertTrue(best_bid.displayed_quantity == 10)
        self.assertTrue(best_bid.show_quantity == 10)

    def test_PassiveIcebergAsk(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00, iceberg_flag=True,
                             displayed_quantity=10)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 0)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 50)
        self.assertTrue(best_ask.displayed_quantity == 10)
        self.assertTrue(best_ask.show_quantity == 10)

    def test_PassiveIcebergPartialTrade_1(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00, iceberg_flag=True,
                             displayed_quantity=10)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 5, 100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 1)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 45)
        self.assertTrue(best_ask.displayed_quantity == 10)
        self.assertTrue(best_ask.show_quantity == 5)

    def test_PassiveIcebergPartialTrade_2(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 50, 100.00, iceberg_flag=True,
                             displayed_quantity=10)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 19, 100.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 1)
        self.assertTrue(len(exchange.trades) == 1)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 31)
        self.assertTrue(best_ask.displayed_quantity == 10)
        self.assertTrue(best_ask.show_quantity == 1)

        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 2, 100.00)

        best_ask = exchange.orderbooks['BTC'].best_ask()
        self.assertTrue(best_ask.total_quantity == 29)
        self.assertTrue(best_ask.displayed_quantity == 10)
        self.assertTrue(best_ask.show_quantity == 9)

    def test_PassiveIcebergFullTrade(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 25, 100.00, iceberg_flag=True,
                             displayed_quantity=5)
        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 25, 101.00, iceberg_flag=True,
                             displayed_quantity=5)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 102.00)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 0)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 2)

    def test_AggressiveIcebergPartialTrade(self):
        exchange = MatchingEngine()
        client_1 = Client(client_name='John Adams')

        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 26, 100.00)

        client_2 = Client(client_name='Jack Jones')
        client_2.place_order(exchange, 'BTC', OrderType.LIMIT, Side.BUY, 50, 102.00, iceberg_flag=True,
                             displayed_quantity=10)

        self.assertTrue(len(exchange.orderbooks['BTC'].bids) == 1)
        self.assertTrue(len(exchange.orderbooks['BTC'].asks) == 0)
        self.assertTrue(len(exchange.trades) == 1)

        best_bid = exchange.orderbooks['BTC'].best_bid()

        self.assertTrue(best_bid.total_quantity == 24)
        self.assertTrue(best_bid.displayed_quantity == 10)
        self.assertTrue(best_bid.show_quantity == 4)

        client_1.place_order(exchange, 'BTC', OrderType.LIMIT, Side.SELL, 5, 102.00)

        best_bid = exchange.orderbooks['BTC'].best_bid()

        self.assertTrue(best_bid.total_quantity == 19)
        self.assertTrue(best_bid.displayed_quantity == 10)
        self.assertTrue(best_bid.show_quantity == 9)


if __name__ == '__main__':
    unittest.main()
