from datetime import datetime


class Trade:
    def __init__(self,
                 trade_id: str,
                 client_id: str,
                 instrument: str,
                 price: float,
                 quantity: int,
                 order_id_b: str,
                 order_id_a: str):

        self.trade_id = trade_id
        self.client_id = client_id
        self.instrument = instrument
        self.price = price
        self.quantity = quantity
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")
        self.order_id_b = order_id_b
        self.order_id_a = order_id_a

    def __repr__(self):
        return f'Trade ID: {self.trade_id}, Client: {self.client_id} Instrument: {self.instrument}, ' \
               f'Price: {self.price}, Quantity: {self.quantity}, Matched Orders: ({self.order_id_b}, {self.order_id_a})'
