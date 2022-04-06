from collections import defaultdict
from itertools import zip_longest
import math
from engine.src.enums import Side
from engine.src.order import Order


class OrderBook:
    def __init__(self, instrument: str, bids: list = None, asks: list = None):

        if bids is None:
            bids = []
        if asks is None:
            asks = []

        self.instrument = instrument

        self._bids = sorted(bids, key=lambda order: (-order.price, order.timestamp))
        self._asks = sorted(asks, key=lambda order: (order.price, order.timestamp))

    def __len__(self):
        return len(self._bids) + len(self._asks)

    @property
    def bids(self):
        return self._bids

    @property
    def asks(self):
        return self._asks

    def add_order(self, order: Order):
        """
        Adds the order to the OrderBook and sorts it

        :param order: Order object to be added to the OrderBook
        """
        if order.side == Side.BUY:
            self._bids.append(order)
            self._bids.sort(key=lambda elem: (-elem.price, elem.timestamp))
        elif order.side == Side.SELL:
            self._asks.append(order)
            self._asks.sort(key=lambda elem: (elem.price, elem.timestamp))

    def remove_order(self, order: Order):
        """
        Removes the order from the OrderBook

        :param order: Order object to be removed from OrderBook
        """
        if order.side == Side.BUY and order in self._bids:
            self._bids.remove(order)
        elif order.side == Side.SELL and order in self._asks:
            self._asks.remove(order)

    def modify_order(self,
                     searched_id: str,
                     side: Side,
                     modified_price: float,
                     modified_qty: float,
                     modified_disp_qty: float = None):
        """
        Allows for order parameters' modification

        :param searched_id: ID of the searched order
        :param side: Side of the searched order
        :param modified_price: New order price
        :param modified_qty: New order quantity
        :param modified_disp_qty: New displayed quantity (applicable only to Iceberg orders)
        """
        if side == Side.BUY:
            try:
                # Search for the specific order
                idx = self._bids.index(next(order for order in self._bids if order.order_id == searched_id))
            except (ValueError, StopIteration):
                print('Order not present in the order book')
            else:
                # Modify the order price and/or quantity
                self._bids[idx].price, self._bids[idx].total_quantity = modified_price, modified_qty

                if modified_disp_qty and self._bids[idx].iceberg_flag is True:
                    self._bids[idx].displayed_quantity, self._bids[idx].show_quantity = modified_disp_qty

                # As the order was modified, generate a new timestamp for it and sort the OrderBook
                self._bids[idx].update_timestamp()
                self._bids.sort(key=lambda order: (-order.price, order.timestamp))

        elif side == Side.SELL:
            try:
                # Search for the specific order
                idx = self._asks.index(next(order for order in self._asks if order.order_id == searched_id))
            except (ValueError, StopIteration):
                print('Order not present in the order book')
            else:
                # Modify the order price and/or quantity
                self._asks[idx].price, self._asks[idx].total_quantity = modified_price, modified_qty

                if modified_disp_qty and self._asks[idx].iceberg_flag is True:
                    self._asks[idx].displayed_quantity, self._asks[idx].show_quantity = modified_disp_qty

                # As the order was modified, generate a new timestamp for it and sort the OrderBook
                self._asks[idx].update_timestamp()
                self._asks.sort(key=lambda order: (order.price, order.timestamp))

    def best_bid(self):
        """Gets the best working bid in the OrderBook"""
        try:
            return self._bids[0]
        except IndexError:
            return None

    def best_ask(self):
        """Gets the best working ask in the OrderBook"""
        try:
            return self._asks[0]
        except IndexError:
            return None

    def best_bid_price(self) -> float:
        """Gets the price of best bid"""
        try:
            return self._bids[0].price
        except IndexError:
            return 0

    def best_ask_price(self) -> float:
        """Gets the price of best ask"""
        try:
            return self._asks[0].price
        except IndexError:
            return math.inf

    def get_level_quantity(self, side: Side, price: float) -> int:
        """Method gets the lot quantity at the given price level"""
        qty = 0
        if side == Side.BUY:
            for order in self._bids:
                qty += order.total_quantity if order.price == price else 0
        elif side == Side.Sell:
            for order in self._asks:
                qty += order.total_quantity if order.price == price else 0
        return qty

    def get_levels_quantity(self, side: Side, threshold_price: float) -> int:
        """
        Method sums up and returns the lot quantity for all levels until selected threshold_price.
        Necessary for proper processing of Fill-or-Kill orders

        :param side: Side of the OrderBook to search
        :param threshold_price: Price until which the OrderBook should be searched
        :return: int
        """
        qty = 0
        if side == Side.BUY:
            for order in self._bids:
                qty += order.total_quantity if order.price >= threshold_price else 0
        elif side == Side.SELL:
            for order in self._asks:
                qty += order.total_quantity if order.price <= threshold_price else 0
        return qty

    def get_client_orders(self, searched_id: str) -> tuple:
        """
        Function returns all orders that are currently working for a given user

        :param searched_id: Client ID to be searched for
        :return: tuple
        """
        bids = [order for order in self._bids if order.client_id == searched_id]
        asks = [order for order in self._asks if order.client_id == searched_id]
        return bids, asks

    def show_book(self, cumulative: bool = True):
        """
        Prints the OrderBook in the console. Used to emulate client's GUI and for manual testing

        :param cumulative: If True the function will print all the orders cumulated on the same level,
               otherwise orders will be printed exactly as they appear in the OrderBook.
        """
        print("+-----------------------------------------+")
        print(f"+                   {self.instrument}                   +")
        print("+-----------------------------------------+")
        print("|         BUY        |        SELL        |")
        print("| Quantity | Price   |  Price  | Quantity |")
        print("+----------+---------+---------+----------+")

        if cumulative:
            grouped_bids = defaultdict(list)
            grouped_asks = defaultdict(list)

            for order in self._bids:
                grouped_bids[order.price].append(order)

            for order in self._asks:
                grouped_asks[order.price].append(order)

            grouped_bids = sorted(grouped_bids.items(), reverse=True)
            grouped_asks = sorted(grouped_asks.items())

            for bids, asks in zip_longest(grouped_bids, grouped_asks):
                if bids and asks:
                    print(f"    {sum(bid.show_quantity for bid in bids[1])}        {bids[0]}      {asks[0]}        {sum(ask.show_quantity for ask in asks[1])}     ")
                elif bids:
                    print(f"    {sum(bid.show_quantity for bid in bids[1])}        {bids[0]}                       ")
                elif asks:
                    print(f"                        {asks[0]}        {sum(ask.show_quantity for ask in asks[1])}     ")

        else:
            for bid, ask in zip_longest(self._bids, self._asks):
                if bid and ask:
                    print(f"    {bid.show_quantity}        {bid.price}      {ask.price}        {ask.show_quantity}     ")
                elif bid:
                    print(f"    {bid.show_quantity}        {bid.price}                       ")
                elif ask:
                    print(f"                        {ask.price}        {ask.show_quantity}     ")
