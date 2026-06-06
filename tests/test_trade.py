"""
Unit tests for Trade model in Cyphernomics Quant Engine.

Tests cover trade creation, validation, state transitions, and P&L calculations.
"""

import pytest
from datetime import datetime, timedelta

from core.models.trade import Trade
from core.models.enums import TradeStatus, TradeDirection, OrderType, ExitReason


class TestTradeCreation:
    """Test trade creation and initialization."""
    
    def test_trade_creation_long(self) -> None:
        """Test creating a valid LONG trade."""
        trade = Trade(
            trade_id="TRADE_001",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        assert trade.trade_id == "TRADE_001"
        assert trade.symbol == "BTC/USDT"
        assert trade.direction == TradeDirection.LONG
        assert trade.entry_price == 50000.0
        assert trade.quantity == 1.0
        assert trade.status == TradeStatus.PENDING
    
    def test_trade_creation_short(self) -> None:
        """Test creating a valid SHORT trade."""
        trade = Trade(
            trade_id="TRADE_002",
            symbol="ETH/USDT",
            direction=TradeDirection.SHORT,
            entry_price=3000.0,
            entry_time=datetime.now(),
            quantity=10.0,
            stop_price=3100.0,
            take_profit_price=2900.0,
        )
        
        assert trade.direction == TradeDirection.SHORT
        assert trade.stop_price == 3100.0
        assert trade.take_profit_price == 2900.0
    
    def test_trade_invalid_entry_price(self) -> None:
        """Test that negative entry price raises ValueError."""
        with pytest.raises(ValueError, match="Entry price must be positive"):
            Trade(
                trade_id="TRADE_003",
                symbol="BTC/USDT",
                direction=TradeDirection.LONG,
                entry_price=-50000.0,
                entry_time=datetime.now(),
                quantity=1.0,
                stop_price=49000.0,
                take_profit_price=51000.0,
            )
    
    def test_trade_invalid_quantity(self) -> None:
        """Test that non-positive quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            Trade(
                trade_id="TRADE_004",
                symbol="BTC/USDT",
                direction=TradeDirection.LONG,
                entry_price=50000.0,
                entry_time=datetime.now(),
                quantity=0.0,
                stop_price=49000.0,
                take_profit_price=51000.0,
            )


class TestLongTradeValidation:
    """Test LONG trade-specific validation."""
    
    def test_long_stop_loss_must_be_below_entry(self) -> None:
        """Test that LONG stop loss must be below entry price."""
        with pytest.raises(ValueError, match="stop_loss .* must be below entry_price"):
            Trade(
                trade_id="TRADE_005",
                symbol="BTC/USDT",
                direction=TradeDirection.LONG,
                entry_price=50000.0,
                entry_time=datetime.now(),
                quantity=1.0,
                stop_price=50100.0,  # Above entry - invalid for LONG
                take_profit_price=51000.0,
            )
    
    def test_long_take_profit_must_be_above_entry(self) -> None:
        """Test that LONG take profit must be above entry price."""
        with pytest.raises(ValueError, match="take_profit .* must be above entry_price"):
            Trade(
                trade_id="TRADE_006",
                symbol="BTC/USDT",
                direction=TradeDirection.LONG,
                entry_price=50000.0,
                entry_time=datetime.now(),
                quantity=1.0,
                stop_price=49000.0,
                take_profit_price=50000.0,  # Not above entry - invalid for LONG
            )
    
    def test_long_valid_levels(self) -> None:
        """Test valid stop/take profit levels for LONG."""
        trade = Trade(
            trade_id="TRADE_007",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        assert trade.stop_price < trade.entry_price
        assert trade.take_profit_price > trade.entry_price


class TestShortTradeValidation:
    """Test SHORT trade-specific validation."""
    
    def test_short_stop_loss_must_be_above_entry(self) -> None:
        """Test that SHORT stop loss must be above entry price."""
        with pytest.raises(ValueError, match="stop_loss .* must be above entry_price"):
            Trade(
                trade_id="TRADE_008",
                symbol="BTC/USDT",
                direction=TradeDirection.SHORT,
                entry_price=50000.0,
                entry_time=datetime.now(),
                quantity=1.0,
                stop_price=49000.0,  # Below entry - invalid for SHORT
                take_profit_price=49000.0,
            )
    
    def test_short_take_profit_must_be_below_entry(self) -> None:
        """Test that SHORT take profit must be below entry price."""
        with pytest.raises(ValueError, match="take_profit .* must be below entry_price"):
            Trade(
                trade_id="TRADE_009",
                symbol="BTC/USDT",
                direction=TradeDirection.SHORT,
                entry_price=50000.0,
                entry_time=datetime.now(),
                quantity=1.0,
                stop_price=51000.0,
                take_profit_price=50000.0,  # Not below entry - invalid for SHORT
            )
    
    def test_short_valid_levels(self) -> None:
        """Test valid stop/take profit levels for SHORT."""
        trade = Trade(
            trade_id="TRADE_010",
            symbol="BTC/USDT",
            direction=TradeDirection.SHORT,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=51000.0,
            take_profit_price=49000.0,
        )
        
        assert trade.stop_price > trade.entry_price
        assert trade.take_profit_price < trade.entry_price


class TestTradeStateTransitions:
    """Test trade lifecycle and state transitions."""
    
    def test_trade_open_from_pending(self) -> None:
        """Test opening a PENDING trade."""
        trade = Trade(
            trade_id="TRADE_011",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        assert trade.status == TradeStatus.PENDING
        trade.open_position()
        assert trade.status == TradeStatus.OPEN
    
    def test_cannot_open_already_open_trade(self) -> None:
        """Test that opening an already open trade raises error."""
        trade = Trade(
            trade_id="TRADE_012",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        
        with pytest.raises(ValueError, match="Only PENDING trades can be opened"):
            trade.open_position()
    
    def test_close_trade_calculates_pnl(self) -> None:
        """Test closing a trade and verifying P&L calculation."""
        trade = Trade(
            trade_id="TRADE_013",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        
        exit_time = datetime.now() + timedelta(hours=2)
        trade.close_position(
            exit_price=51000.0,
            exit_time=exit_time,
            exit_reason=ExitReason.TAKE_PROFIT,
            commission=10.0
        )
        
        assert trade.status == TradeStatus.CLOSED
        assert trade.exit_price == 51000.0
        assert trade.exit_reason == ExitReason.TAKE_PROFIT
    
    def test_cannot_close_pending_trade(self) -> None:
        """Test that closing a PENDING trade raises error."""
        trade = Trade(
            trade_id="TRADE_014",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        with pytest.raises(ValueError, match="Only OPEN trades can be closed"):
            trade.close_position(
                exit_price=51000.0,
                exit_time=datetime.now(),
                exit_reason=ExitReason.TAKE_PROFIT,
            )


class TestPnLCalculations:
    """Test P&L calculation accuracy."""
    
    def test_long_pnl_profit(self) -> None:
        """Test P&L calculation for profitable LONG trade."""
        trade = Trade(
            trade_id="TRADE_015",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=2.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=51000.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.TAKE_PROFIT,
            commission=0.0,
        )
        
        # Expected: (51000 - 50000) * 2 = 2000
        assert trade.pnl == 2000.0
    
    def test_long_pnl_loss(self) -> None:
        """Test P&L calculation for losing LONG trade."""
        trade = Trade(
            trade_id="TRADE_016",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=49500.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.STOP_LOSS,
            commission=0.0,
        )
        
        # Expected: (49500 - 50000) * 1 = -500
        assert trade.pnl == -500.0
    
    def test_short_pnl_profit(self) -> None:
        """Test P&L calculation for profitable SHORT trade."""
        trade = Trade(
            trade_id="TRADE_017",
            symbol="BTC/USDT",
            direction=TradeDirection.SHORT,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=51000.0,
            take_profit_price=49000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=49000.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.TAKE_PROFIT,
            commission=0.0,
        )
        
        # Expected: (50000 - 49000) * 1 = 1000
        assert trade.pnl == 1000.0
    
    def test_short_pnl_loss(self) -> None:
        """Test P&L calculation for losing SHORT trade."""
        trade = Trade(
            trade_id="TRADE_018",
            symbol="BTC/USDT",
            direction=TradeDirection.SHORT,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=2.0,
            stop_price=51000.0,
            take_profit_price=49000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=50500.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.STOP_LOSS,
            commission=0.0,
        )
        
        # Expected: (50000 - 50500) * 2 = -1000
        assert trade.pnl == -1000.0
    
    def test_pnl_with_commission(self) -> None:
        """Test P&L calculation accounting for commissions."""
        trade = Trade(
            trade_id="TRADE_019",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=51000.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.TAKE_PROFIT,
            commission=10.0,
        )
        
        # Expected: (51000 - 50000) * 1 - 10 = 990
        assert trade.pnl == 990.0
    
    def test_pnl_percent_calculation(self) -> None:
        """Test P&L percentage calculation."""
        trade = Trade(
            trade_id="TRADE_020",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=100.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=90.0,
            take_profit_price=110.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=110.0,
            exit_time=datetime.now() + timedelta(hours=1),
            exit_reason=ExitReason.TAKE_PROFIT,
            commission=0.0,
        )
        
        # Expected: 10% return
        assert trade.pnl_percent == pytest.approx(10.0)


class TestRiskRewardRatio:
    """Test risk-reward ratio calculations."""
    
    def test_rr_ratio_calculation_long(self) -> None:
        """Test R:R ratio calculation for LONG trade."""
        trade = Trade(
            trade_id="TRADE_021",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=100.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=90.0,
            take_profit_price=120.0,
        )
        
        # Risk: 100 - 90 = 10
        # Reward: 120 - 100 = 20
        # R:R = 20 / 10 = 2.0
        assert trade.risk_reward_ratio == pytest.approx(2.0)
    
    def test_rr_ratio_calculation_short(self) -> None:
        """Test R:R ratio calculation for SHORT trade."""
        trade = Trade(
            trade_id="TRADE_022",
            symbol="BTC/USDT",
            direction=TradeDirection.SHORT,
            entry_price=100.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=110.0,
            take_profit_price=80.0,
        )
        
        # Risk: 110 - 100 = 10
        # Reward: 100 - 80 = 20
        # R:R = 20 / 10 = 2.0
        assert trade.risk_reward_ratio == pytest.approx(2.0)


class TestTradeProperties:
    """Test trade property getters."""
    
    def test_is_open_property(self) -> None:
        """Test is_open property."""
        trade = Trade(
            trade_id="TRADE_023",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        assert not trade.is_open
        trade.open_position()
        assert trade.is_open
    
    def test_is_closed_property(self) -> None:
        """Test is_closed property."""
        trade = Trade(
            trade_id="TRADE_024",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        assert not trade.is_closed
        trade.open_position()
        trade.close_position(
            exit_price=51000.0,
            exit_time=datetime.now(),
            exit_reason=ExitReason.TAKE_PROFIT,
        )
        assert trade.is_closed
    
    def test_get_risk_amount(self) -> None:
        """Test risk amount calculation."""
        trade = Trade(
            trade_id="TRADE_025",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=2.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        # Risk: (50000 - 49000) * 2 = 2000
        assert trade.get_risk_amount() == 2000.0
    
    def test_get_reward_amount(self) -> None:
        """Test reward amount calculation."""
        trade = Trade(
            trade_id="TRADE_026",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime.now(),
            quantity=2.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        # Reward: (51000 - 50000) * 2 = 2000
        assert trade.get_reward_amount() == 2000.0
    
    def test_get_duration(self) -> None:
        """Test trade duration calculation."""
        now = datetime.now()
        entry_time = now
        exit_time = now + timedelta(hours=5, minutes=30)
        
        trade = Trade(
            trade_id="TRADE_027",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=entry_time,
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position(entry_time=entry_time)
        trade.close_position(
            exit_price=51000.0,
            exit_time=exit_time,
            exit_reason=ExitReason.TAKE_PROFIT,
        )
        
        duration = trade.get_duration()
        assert duration == pytest.approx(5.5, rel=0.01)


class TestTradeToDict:
    """Test trade serialization."""
    
    def test_to_dict_pending_trade(self) -> None:
        """Test converting pending trade to dictionary."""
        trade = Trade(
            trade_id="TRADE_028",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime(2024, 1, 1, 12, 0, 0),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade_dict = trade.to_dict()
        
        assert trade_dict["trade_id"] == "TRADE_028"
        assert trade_dict["symbol"] == "BTC/USDT"
        assert trade_dict["direction"] == "LONG"
        assert trade_dict["status"] == "PENDING"
    
    def test_to_dict_closed_trade(self) -> None:
        """Test converting closed trade to dictionary."""
        trade = Trade(
            trade_id="TRADE_029",
            symbol="BTC/USDT",
            direction=TradeDirection.LONG,
            entry_price=50000.0,
            entry_time=datetime(2024, 1, 1, 12, 0, 0),
            quantity=1.0,
            stop_price=49000.0,
            take_profit_price=51000.0,
        )
        
        trade.open_position()
        trade.close_position(
            exit_price=51000.0,
            exit_time=datetime(2024, 1, 1, 13, 0, 0),
            exit_reason=ExitReason.TAKE_PROFIT,
        )
        
        trade_dict = trade.to_dict()
        
        assert trade_dict["status"] == "CLOSED"
        assert trade_dict["exit_price"] == 51000.0
        assert trade_dict["pnl"] == 1000.0
