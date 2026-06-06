"""
Enumeration types for Cyphernomics Quant Engine.

Defines common enums used across the platform.
"""

from enum import Enum


class TradeStatus(str, Enum):
    """Trade lifecycle status."""
    
    PENDING = "PENDING"          # Order placed, awaiting fill
    OPEN = "OPEN"                # Position opened
    CLOSED = "CLOSED"            # Position closed with P&L
    ABANDONED = "ABANDONED"      # Signal cancelled before entry
    CANCELLED = "CANCELLED"      # Order cancelled


class TradeDirection(str, Enum):
    """Trade direction."""
    
    LONG = "LONG"                # Bullish position
    SHORT = "SHORT"              # Bearish position


class OrderType(str, Enum):
    """Order types."""
    
    MARKET = "MARKET"            # Immediate execution at market price
    LIMIT = "LIMIT"              # Execution at specified price or better


class ExitReason(str, Enum):
    """Reason for trade exit."""
    
    STOP_LOSS = "STOP_LOSS"      # Stopped out at loss
    TAKE_PROFIT = "TAKE_PROFIT"  # Target reached
    TIME_EXIT = "TIME_EXIT"      # Maximum holding period exceeded
    SIGNAL_EXIT = "SIGNAL_EXIT"  # Reverse signal generated
    MANUAL_EXIT = "MANUAL_EXIT"  # Manual closure
