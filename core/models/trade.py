"""
Trade model for Cyphernomics Quant Engine.

Represents a single trade with entry/exit logic, P&L calculations, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from .enums import TradeStatus, TradeDirection, OrderType, ExitReason


@dataclass
class Trade:
    """
    Represents a single trade in the trading system.
    
    Attributes:
        trade_id: Unique identifier for the trade
        symbol: Trading pair (e.g., 'BTC/USDT')
        direction: LONG or SHORT
        entry_price: Price at which position opened
        entry_time: Timestamp of entry
        quantity: Number of units traded
        stop_price: Stop loss price
        take_profit_price: Target take profit price
        order_type: MARKET or LIMIT
        status: Current trade status
        exit_price: Price at which position closed (if closed)
        exit_time: Timestamp of exit (if closed)
        exit_reason: Reason for exit (if closed)
        commission: Trading fees paid
        slippage: Price slippage cost
        pnl: Profit/Loss in absolute terms
        pnl_percent: Profit/Loss as percentage
        pnl_pips: Profit/Loss in pips (BTC: sat, etc)
        risk_reward_ratio: Actual RR ratio achieved
        timeframe: Trading timeframe (e.g., '15m', '1h')
        notes: Additional trade notes
    """
    
    trade_id: str
    symbol: str
    direction: TradeDirection
    entry_price: float
    entry_time: datetime
    quantity: float
    stop_price: float
    take_profit_price: float
    order_type: OrderType = OrderType.MARKET
    status: TradeStatus = TradeStatus.PENDING
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[ExitReason] = None
    commission: float = 0.0
    slippage: float = 0.0
    pnl: float = field(default=0.0, init=False)
    pnl_percent: float = field(default=0.0, init=False)
    pnl_pips: float = field(default=0.0, init=False)
    risk_reward_ratio: Optional[float] = field(default=None, init=False)
    timeframe: str = "1h"
    notes: str = ""
    
    def __post_init__(self) -> None:
        """Validate trade parameters after initialization."""
        self._validate()
        self._calculate_theoretical_rr()
    
    def _validate(self) -> None:
        """Validate trade parameters."""
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.stop_price <= 0:
            raise ValueError("Stop price must be positive")
        if self.take_profit_price <= 0:
            raise ValueError("Take profit price must be positive")
        
        if self.direction == TradeDirection.LONG:
            if self.stop_price >= self.entry_price:
                raise ValueError(
                    "For LONG: stop price must be below entry price"
                )
            if self.take_profit_price <= self.entry_price:
                raise ValueError(
                    "For LONG: take profit price must be above entry price"
                )
        else:  # SHORT
            if self.stop_price <= self.entry_price:
                raise ValueError(
                    "For SHORT: stop price must be above entry price"
                )
            if self.take_profit_price >= self.entry_price:
                raise ValueError(
                    "For SHORT: take profit price must be below entry price"
                )
    
    def _calculate_theoretical_rr(self) -> None:
        """Calculate theoretical risk-to-reward ratio."""
        risk = abs(self.entry_price - self.stop_price)
        reward = abs(self.take_profit_price - self.entry_price)
        
        if risk > 0:
            self.risk_reward_ratio = reward / risk
    
    def open_position(
        self,
        actual_entry_price: Optional[float] = None,
        entry_time: Optional[datetime] = None
    ) -> None:
        """
        Mark position as opened after fill confirmation.
        
        Args:
            actual_entry_price: Actual fill price (may differ from entry_price due to slippage)
            entry_time: Actual entry timestamp
        """
        if self.status != TradeStatus.PENDING:
            raise ValueError("Only PENDING trades can be opened")
        
        if actual_entry_price:
            self.slippage = abs(
                actual_entry_price - self.entry_price
            )
            self.entry_price = actual_entry_price
        
        if entry_time:
            self.entry_time = entry_time
        
        self.status = TradeStatus.OPEN
    
    def close_position(
        self,
        exit_price: float,
        exit_time: datetime,
        exit_reason: ExitReason,
        commission: float = 0.0
    ) -> None:
        """
        Close the open position and calculate P&L.
        
        Args:
            exit_price: Price at which position closed
            exit_time: Timestamp of exit
            exit_reason: Reason for exiting trade
            commission: Trading commissions/fees
        
        Raises:
            ValueError: If trade is not open or exit_price is invalid
        """
        if self.status != TradeStatus.OPEN:
            raise ValueError("Only OPEN trades can be closed")
        
        if exit_price <= 0:
            raise ValueError("Exit price must be positive")
        
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = exit_reason
        self.commission = commission
        
        self._calculate_pnl()
        self.status = TradeStatus.CLOSED
    
    def _calculate_pnl(self) -> None:
        """Calculate profit/loss in absolute and percentage terms."""
        if not self.exit_price:
            raise ValueError("Cannot calculate P&L without exit price")
        
        if self.direction == TradeDirection.LONG:
            price_difference = self.exit_price - self.entry_price
        else:  # SHORT
            price_difference = self.entry_price - self.exit_price
        
        # Calculate P&L in absolute terms
        gross_pnl = price_difference * self.quantity
        self.pnl = gross_pnl - self.commission - self.slippage
        
        # Calculate P&L in percentage terms
        position_value = self.entry_price * self.quantity
        if position_value > 0:
            self.pnl_percent = (self.pnl / position_value) * 100
        
        # Calculate P&L in pips (smallest unit)
        self.pnl_pips = price_difference
    
    def is_profitable(self) -> bool:
        """Check if trade ended profitably."""
        if self.status != TradeStatus.CLOSED:
            raise ValueError("Cannot check profitability of non-closed trade")
        return self.pnl > 0
    
    def get_duration(self) -> Optional[float]:
        """
        Get trade duration in hours.
        
        Returns:
            Duration in hours, or None if trade not closed
        """
        if self.status != TradeStatus.CLOSED or not self.exit_time:
            return None
        
        duration = self.exit_time - self.entry_time
        return duration.total_seconds() / 3600
    
    def get_risk_amount(self) -> float:
        """Calculate absolute risk amount in base currency."""
        return abs(self.entry_price - self.stop_price) * self.quantity
    
    def get_reward_amount(self) -> float:
        """Calculate absolute reward amount in base currency."""
        return abs(self.take_profit_price - self.entry_price) * self.quantity
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary format."""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "direction": self.direction.value,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "quantity": self.quantity,
            "stop_price": self.stop_price,
            "take_profit_price": self.take_profit_price,
            "order_type": self.order_type.value,
            "status": self.status.value,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_reason": self.exit_reason.value if self.exit_reason else None,
            "commission": self.commission,
            "slippage": self.slippage,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "pnl_pips": self.pnl_pips,
            "risk_reward_ratio": self.risk_reward_ratio,
            "timeframe": self.timeframe,
            "notes": self.notes,
        }
    
    def __str__(self) -> str:
        """String representation of trade."""
        return (
            f"Trade(id={self.trade_id}, {self.direction.value} {self.symbol}, "
            f"entry={self.entry_price}, status={self.status.value}, "
            f"pnl={self.pnl:.2f} ({self.pnl_percent:.2f}%))"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return self.__str__()
