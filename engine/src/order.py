from datetime import datetime
import math
from random import randint
from engine.src.enums import Side, OrderType


class Order:
    def __init__(self,
                 client_id: str,
                 instrument: str,
                 order_type: OrderType,
                 side: Side,
                 total_quantity: int,
                 price: float,
                 iceberg_flag: bool,
                 displayed_quantity: int,
                 fok_flag: bool,
                 stop_flag: bool,
                 trigger_price: float):

        # Obligatory variables
        self.client_id = client_id
        self.instrument = instrument
        self.order_type = order_type
        self.side = side
        self.total_quantity = total_quantity

        # ID generated just for simulation purposes, in PROD this should be communicated with the database
        self.order_id = f'o{randint(0, 100000):06}'

        # Variables necessary for the iceberg orders
        self.iceberg_flag = iceberg_flag
        self.displayed_quantity = displayed_quantity if displayed_quantity is not None and self.iceberg_flag is True else total_quantity
        self.show_quantity = displayed_quantity if displayed_quantity is not None and self.iceberg_flag is True else total_quantity

        # Fill or Kill order flag
        self.fok_flag = fok_flag

        # STOP order flag and the associated trigger price
        self.stop_flag = stop_flag
        self.trigger_price = trigger_price
        if self.stop_flag:
            assert self.trigger_price, 'Trigger price needs to be defined for STOP orders'

        # Order creation timestamp necessary for queuing the orders in OrderBook
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")

        # For MARKET order price is either infinity (bid) or 0 (ask)
        if self.order_type == OrderType.MARKET:
            self.price = math.inf if side == Side.BUY else 0

        elif self.order_type == OrderType.LIMIT:
            assert price, f'Price needs to be defined for the {self.order_type} order'
            self.price = price

        # Side and quantity assertions
        assert self.total_quantity > 0, 'Quantity has to be positive'
        assert self.side in (Side.BUY, Side.SELL), f'Invalid order side: {self.side}'

        # Display Quantity Assertions
        assert self.displayed_quantity <= self.total_quantity, 'Displayed quantity cannot be larger than real order size'
        assert self.displayed_quantity > 0, 'Displayed quantity has to be at least 1'

    def __repr__(self):
        return f'ID: {self.order_id}, Instrument: {self.instrument}, Type: {self.order_type}, Price: {self.price}, ' \
               f'Quantity: {self.total_quantity}'

    def deactivate_stop_flag(self):
        """Function deactivates the flag enabling the engine to process the order when the trigger price gets traded"""
        self.stop_flag = False

    def update_timestamp(self):
        """Function used to update order's timestamp in case it's modified"""
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")
