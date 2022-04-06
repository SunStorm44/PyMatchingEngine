from engine.src.order import Order
from engine.src.orderbook import OrderBook
from engine.src.trade import Trade
from engine.src.enums import Side, OrderType


class MatchingEngine:
    def __init__(self):
        self._orderbooks = {}
        self._trades = []
        self._stop_bids = {}
        self._stop_asks = {}
        # Counter used to generate unique trade IDs
        self.__counter = 1

    @property
    def orderbooks(self):
        return self._orderbooks

    @property
    def trades(self):
        return self._trades

    @property
    def stop_bids(self):
        return self._stop_bids

    @property
    def stop_asks(self):
        return self._stop_asks

    def match_order(self, order: Order):
        """
        Main matching function

        :param order: New order reaching the engine
        """
        # Check if OrderBook for given instrument is already in place, if not create one
        instr = order.instrument
        if instr not in self._orderbooks:
            self._orderbooks[instr] = OrderBook(instr)

        filled = 0
        cleared_levels = []

        # If the order is a STOP order, don't add it to OrderBook but save it in a queue where it would be waiting for a trigger price to trade
        if order.stop_flag:
            self.add_stop(order)

        elif order.side == Side.BUY:

            for ask in self._orderbooks[instr].asks:

                # Not enough quantity to fill the whole Fill or Kill order
                if order.fok_flag and self.orderbooks[order.instrument].get_levels_quantity(Side.SELL, order.price) < order.total_quantity:
                    break

                # Existing price is too high, stop filling and work the full/remaining qty
                if ask.price > order.price:
                    break

                # Order was filled completely
                if filled == order.total_quantity:
                    break

                # Whole level gets filled
                if ask.total_quantity <= order.total_quantity - filled:
                    filled += ask.total_quantity
                    trade = Trade(trade_id=f'c{self.__counter:06}',
                                  client_id=order.client_id,
                                  instrument=order.instrument,
                                  price=ask.price,
                                  quantity=ask.total_quantity,
                                  order_id_b=order.order_id,
                                  order_id_a=ask.order_id)
                    cleared_levels.append(ask)
                    self._trades.append(trade)

                # Not the whole level gets filled
                elif ask.total_quantity > order.total_quantity - filled:
                    size_traded = order.total_quantity - filled
                    filled += size_traded
                    trade = Trade(trade_id='t' + str(self.__counter),
                                  client_id=order.client_id,
                                  instrument=order.instrument,
                                  price=ask.price,
                                  quantity=size_traded,
                                  order_id_b=order.order_id,
                                  order_id_a=ask.order_id)
                    self._trades.append(trade)

                    ask.total_quantity -= size_traded

                    # Special logic for passive iceberg orders to have the proper qty displayed in the OrderBook
                    if ask.iceberg_flag is True:
                        if size_traded < ask.show_quantity:
                            ask.show_quantity -= size_traded
                        else:
                            qty = size_traded - ask.displayed_quantity
                            ask.show_quantity -= qty
                    else:
                        ask.show_quantity -= size_traded

                self.__counter += 1

            # Not the whole order was filled, add the remaining quantity to the OrderBook
            if filled < order.total_quantity and not order.fok_flag and order.order_type == OrderType.LIMIT:
                order.total_quantity -= filled
                order.displayed_quantity = order.displayed_quantity if order.iceberg_flag is False or order.displayed_quantity <= order.total_quantity else order.total_quantity

                # Special logic for aggressive iceberg orders to have the proper qty displayed in the OrderBook
                if order.iceberg_flag and filled:
                    if filled < order.show_quantity:
                        order.show_quantity -= filled
                    else:
                        order.show_quantity = order.total_quantity % order.displayed_quantity
                else:
                    order.show_quantity -= filled

                self._orderbooks[instr].add_order(order)

            # Remove all traded orders from the OrderBook
            for ask in cleared_levels:
                self._orderbooks[instr].remove_order(ask)

            # If anything traded, check if any stop order was triggered, if yes call the matching engine
            if filled:
                stop_orders = self.get_stops(instrument=order.instrument,
                                             price=self.get_last_trade_price(),
                                             side=order.side)
                for stp_ord in stop_orders:
                    stp_ord.deactivate_stop_flag()
                    self.match_order(stp_ord)

        elif order.side == Side.SELL:
            for bid in self._orderbooks[instr].bids:

                # Not enough quantity to fill the whole Fill or Kill order
                if order.fok_flag and self.orderbooks[order.instrument].get_levels_quantity(Side.BUY, order.price) < order.total_quantity:
                    break

                # Existing price is too high, stop filling and work the full/remaining qty
                if bid.price < order.price:
                    break

                # Order was filled completely
                if filled == order.total_quantity:
                    break

                # Whole level gets filled
                if bid.total_quantity <= order.total_quantity - filled:
                    filled += bid.total_quantity
                    trade = Trade(trade_id='t' + str(self.__counter),
                                  client_id=order.client_id,
                                  instrument=order.instrument,
                                  price=bid.price,
                                  quantity=bid.total_quantity,
                                  order_id_b=bid.order_id,
                                  order_id_a=order.order_id)
                    cleared_levels.append(bid)
                    self._trades.append(trade)

                # Not the whole level gets filled
                elif bid.total_quantity > order.total_quantity - filled:
                    size_traded = order.total_quantity - filled
                    filled += size_traded
                    trade = Trade(trade_id='t' + str(self.__counter),
                                  client_id=order.client_id,
                                  instrument=order.instrument,
                                  price=bid.price,
                                  quantity=size_traded,
                                  order_id_b=bid.order_id,
                                  order_id_a=order.order_id)
                    self._trades.append(trade)

                    bid.total_quantity -= size_traded

                    # Special logic for iceberg orders to have the proper qty displayed in the OrderBook
                    if bid.iceberg_flag is True:
                        if size_traded < bid.show_quantity:
                            bid.show_quantity -= size_traded
                        else:
                            qty = size_traded - bid.displayed_quantity
                            bid.show_quantity -= qty
                    else:
                        bid.show_quantity -= size_traded

            self.__counter += 1

            # Not the whole order was filled, add the remaining quantity to the OrderBook
            if filled < order.total_quantity and not order.fok_flag and order.order_type == OrderType.LIMIT:
                order.total_quantity -= filled
                order.displayed_quantity = order.displayed_quantity if order.iceberg_flag is False or order.displayed_quantity <= order.total_quantity else order.total_quantity

                # Special logic for aggressive iceberg orders to have the proper qty displayed in the OrderBook
                if order.iceberg_flag and filled:
                    if filled < order.show_quantity:
                        order.show_quantity -= filled
                    else:
                        order.show_quantity = order.total_quantity % order.displayed_quantity
                else:
                    order.show_quantity -= filled

                self._orderbooks[instr].add_order(order)

            # Remove all traded orders from the OrderBook
            for bid in cleared_levels:
                self._orderbooks[instr].remove_order(bid)

            # If anything traded check if any stop order was triggered, if yes call the matching engine
            if filled:
                stop_orders = self.get_stops(instrument=order.instrument,
                                             price=self.get_last_trade_price(),
                                             side=order.side)
                for stp_ord in stop_orders:
                    stp_ord.deactivate_stop_flag()
                    self.match_order(stp_ord)

    def add_stop(self, order: Order):
        """
        Method adds al stop orders to special queue where they wait for a trigger price to be traded

        :param order: Stop order to be added to the queue
        """

        if order.side == Side.BUY:
            if order.instrument in self._stop_bids:
                self._stop_bids[order.instrument].append(order)
                self._stop_bids[order.instrument].sort(key=lambda elem: (elem.trigger_price, elem.timestamp))

            else:
                self._stop_bids[order.instrument] = [order]
        elif order.side == Side.SELL:
            if order.instrument in self._stop_asks:
                self._stop_asks[order.instrument].append(order)
                self._stop_asks[order.instrument].sort(key=lambda elem: (-elem.trigger_price, elem.timestamp))

            else:
                self._stop_asks[order.instrument] = [order]

    def get_stops(self, instrument: str, price: float, side: Side) -> list:
        """
        Method used to search the stop queues for any orders that got triggered and return them to the main engine

        :param instrument: Most recently traded instrument
        :param price: Most recently traded price
        :param side: Attacking order's side
        :return: list
        """
        triggered_stops = []

        if side == Side.BUY and instrument in self._stop_bids:
            for stop_order in self._stop_bids[instrument]:
                if stop_order.trigger_price > price:
                    break
                triggered_stops.append(stop_order)
            # If found anything remove it from queue
            if triggered_stops:
                self._stop_bids[instrument] = [elem for elem in self._stop_bids[instrument] if
                                               elem not in triggered_stops]
        elif side == Side.SELL and instrument in self._stop_asks:
            for stop_order in self._stop_asks[instrument]:
                if stop_order.trigger_price < price:
                    break
                triggered_stops.append(stop_order)
            # If found anything remove it from queue
            if triggered_stops:
                self._stop_asks[instrument] = [elem for elem in self._stop_asks[instrument] if
                                               elem not in triggered_stops]

        return triggered_stops

    def get_last_trade_price(self):
        """Method used to get the most recently traded price"""
        try:
            return self._trades[-1].price
        except IndexError:
            return None

    def get_client_trades(self, searched_id: str) -> list:
        """
        Method returns all trades performed by the searched client

        :param searched_id: Client ID to be searched for
        :return: list
        """
        out_trades = []
        for trade in self._trades:
            if trade.client_id == searched_id:
                out_trades.append(trade)
        return out_trades
