"""TO BE COMPLETED"""

from engine.matching_engine import MatchingEngine
from engine.src.order import Order
from random import randint
from engine.src.enums import Side, OrderType


class Client:
    def __init__(self, client_name: str):
        # ID generated just for simulation purposes, in PROD this should be communicated with the database
        self._client_id = f'c{randint(0, 100000):06}'
        self.client_name = client_name

        self.working_orders = []
        self.trade_list = []
        self.positions = []

    @property
    def client_id(self):
        return self._client_id

    def __repr__(self):
        return f'Client ID: {self._client_id}, Name: {self.client_name}'

    def place_order(self,
                    exchange: MatchingEngine,
                    instrument: str,
                    order_type: OrderType,
                    side: Side,
                    total_quantity: int,
                    price: float = None,
                    iceberg_flag: bool = False,
                    displayed_quantity: int = None,
                    fok_flag: bool = False,
                    stop_flag: bool = False,
                    trigger_price: float = None):

        order = Order(self._client_id,
                      instrument,
                      order_type,
                      side,
                      total_quantity,
                      price,
                      iceberg_flag,
                      displayed_quantity,
                      fok_flag,
                      stop_flag,
                      trigger_price)

        exchange.match_order(order)

        return 0

