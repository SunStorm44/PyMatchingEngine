"""Enums used for order side and type selection"""
from enum import Enum


class Side(Enum):
    BUY = 1
    SELL = 2


class OrderType(Enum):
    MARKET = 1
    LIMIT = 2

