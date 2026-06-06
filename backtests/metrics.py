"""
Performance metrics calculation for Cyphernomics Quant Engine.

Computes trading performance statistics including win rate, profit factor,
Sharpe ratio, maximum drawdown, and other key metrics.
"""

import logging
from typing import List, Dict
import numpy as np

from core.models.trade import Trade

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate comprehensive performance metrics from a list of trades.
    """
    
    def __init__(self, trades: List[Trade], initial_capital: float):
        """
        Initialize metrics calculator.
        
        Args:
            trades: List of Trade objects
            initial_capital: Starting account balance
        
        Raises:
            ValueError: If initial_capital is not positive
        """
        if initial_capital <= 0:
            raise ValueError(
                f"Initial capital must be positive, got {initial_capital}"
            )
        
        self.trades = [t for t in trades if t.status.value == "CLOSED"]
        self.initial_capital = initial_capital
        self.total_trades = len(self.trades)
        
        if self.total_trades == 0:
            logger.warning("No closed trades found for metrics calculation")
    
    @property
    def winning_trades(self) -> List[Trade]:
        """Get list of profitable trades."""
        return [t for t in self.trades if t.pnl > 0]
    
    @property
    def losing_trades(self) -> List[Trade]:
        """Get list of losing trades."""
        return [t for t in self.trades if t.pnl < 0]
    
    @property
    def total_pnl(self) -> float:
        """Calculate total P&L across all trades."""
        return sum(t.pnl for t in self.trades)
    
    @property
    def win_count(self) -> int:
        """Total number of winning trades."""
        return len(self.winning_trades)
    
    @property
    def loss_count(self) -> int:
        """Total number of losing trades."""
        return len(self.losing_trades)
    
    @property
    def win_rate(self) -> float:
        """
        Calculate win rate as percentage.
        
        Returns:
            Win rate (0-100), or 0 if no trades
        """
        if self.total_trades == 0:
            return 0.0
        return (self.win_count / self.total_trades) * 100
    
    @property
    def loss_rate(self) -> float:
        """
        Calculate loss rate as percentage.
        
        Returns:
            Loss rate (0-100), or 0 if no trades
        """
        return 100.0 - self.win_rate
    
    @property
    def gross_profit(self) -> float:
        """Sum of all profitable trades."""
        return sum(t.pnl for t in self.winning_trades)
    
    @property
    def gross_loss(self) -> float:
        """Sum of all losing trades (absolute value)."""
        return abs(sum(t.pnl for t in self.losing_trades))
    
    @property
    def profit_factor(self) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Returns:
            Profit factor, or 0 if no losses (all wins)
        
        Interpretation:
            > 2.0 = Excellent
            1.5-2.0 = Good
            1.0-1.5 = Acceptable
            < 1.0 = Not profitable
        """
        if self.gross_loss == 0:
            return float('inf') if self.gross_profit > 0 else 0.0
        return self.gross_profit / self.gross_loss
    
    @property
    def average_win(self) -> float:
        """Average profit per winning trade."""
        if self.win_count == 0:
            return 0.0
        return self.gross_profit / self.win_count
    
    @property
    def average_loss(self) -> float:
        """Average loss per losing trade (positive number)."""
        if self.loss_count == 0:
            return 0.0
        return self.gross_loss / self.loss_count
    
    @property
    def expectancy(self) -> float:
        """
        Calculate expectancy (average P&L per trade).
        
        Returns:
            Average P&L per trade
        """
        if self.total_trades == 0:
            return 0.0
        return self.total_pnl / self.total_trades
    
    @property
    def max_consecutive_wins(self) -> int:
        """Calculate maximum consecutive winning trades."""
        if not self.trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @property
    def max_consecutive_losses(self) -> int:
        """Calculate maximum consecutive losing trades."""
        if not self.trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @property
    def equity_curve(self) -> List[float]:
        """
        Generate equity curve (cumulative balance over time).
        
        Returns:
            List of account balances after each trade
        """
        curve = [self.initial_capital]
        running_balance = self.initial_capital
        
        for trade in self.trades:
            running_balance += trade.pnl
            curve.append(running_balance)
        
        return curve
    
    @property
    def peak_equity(self) -> float:
        """Highest equity reached during trading period."""
        curve = self.equity_curve
        return max(curve) if curve else self.initial_capital
    
    @property
    def maximum_drawdown(self) -> float:
        """
        Calculate maximum drawdown (peak-to-trough decline).
        
        Returns:
            Maximum drawdown as percentage
        """
        curve = self.equity_curve
        if not curve or len(curve) < 2:
            return 0.0
        
        peak = curve[0]
        max_dd = 0.0
        
        for value in curve:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd * 100
    
    @property
    def maximum_drawdown_usd(self) -> float:
        """Maximum drawdown in USD."""
        return (self.maximum_drawdown / 100) * self.peak_equity
    
    @property
    def return_percent(self) -> float:
        """
        Calculate total return as percentage.
        
        Returns:
            Total return (%), positive for gains, negative for losses
        """
        if self.initial_capital <= 0:
            return 0.0
        return (self.total_pnl / self.initial_capital) * 100
    
    def sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted return).
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sharpe ratio (higher is better, >1 is good)
        
        Interpretation:
            > 1.0 = Good
            > 2.0 = Very good
            > 3.0 = Excellent
        """
        if self.total_trades == 0:
            return 0.0
        
        pnl_list = [t.pnl for t in self.trades]
        returns = np.array(pnl_list) / self.initial_capital
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualize assuming ~252 trading days per year
        annual_return = mean_return * 252
        annual_std = std_return * np.sqrt(252)
        
        sharpe = (annual_return - risk_free_rate) / annual_std
        return sharpe
    
    def sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino ratio (return / downside deviation).
        
        Only penalizes downside volatility, not upside.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sortino ratio (higher is better, >1 is good)
        
        Interpretation:
            > 1.0 = Good
            > 2.0 = Very good
            > 3.0 = Excellent
        """
        if self.total_trades == 0:
            return 0.0
        
        pnl_list = [t.pnl for t in self.trades]
        returns = np.array(pnl_list) / self.initial_capital
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        
        # Calculate downside deviation
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            downside_std = 0.0
        else:
            downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return float('inf') if mean_return > 0 else 0.0
        
        # Annualize
        annual_return = mean_return * 252
        annual_downside_std = downside_std * np.sqrt(252)
        
        sortino = (annual_return - risk_free_rate) / annual_downside_std
        return sortino
    
    def cagr(self) -> float:
        """
        Calculate Compound Annual Growth Rate.
        
        Returns:
            CAGR as percentage
        """
        if self.total_trades == 0:
            return 0.0
        
        if not self.trades:
            return 0.0
        
        first_trade = self.trades[0]
        last_trade = self.trades[-1]
        
        if first_trade.exit_time is None or last_trade.exit_time is None:
            return 0.0
        
        trading_period = last_trade.exit_time - first_trade.entry_time
        years = trading_period.total_seconds() / (365.25 * 24 * 3600)
        
        if years <= 0:
            return 0.0
        
        ending_value = self.initial_capital + self.total_pnl
        
        if ending_value <= 0:
            return 0.0
        
        cagr_val = (pow(ending_value / self.initial_capital, 1 / years) - 1) * 100
        return cagr_val
    
    def calmar_ratio(self) -> float:
        """
        Calculate Calmar ratio (return / max drawdown).
        
        Returns:
            Calmar ratio (higher is better)
        
        Interpretation:
            > 1.0 = Good
            > 2.0 = Very good
            > 3.0 = Excellent
        """
        if self.maximum_drawdown == 0:
            return float('inf') if self.return_percent > 0 else 0.0
        return self.return_percent / self.maximum_drawdown
    
    def recovery_factor(self) -> float:
        """
        Calculate recovery factor (total profit / max drawdown).
        
        Returns:
            Recovery factor (higher is better)
        """
        if self.maximum_drawdown_usd == 0:
            return float('inf') if self.total_pnl > 0 else 0.0
        return self.total_pnl / self.maximum_drawdown_usd
    
    def get_summary(self) -> Dict:
        """
        Get complete performance summary.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.win_count,
            "losing_trades": self.loss_count,
            "win_rate_percent": round(self.win_rate, 2),
            "loss_rate_percent": round(self.loss_rate, 2),
            "total_pnl_usd": round(self.total_pnl, 2),
            "gross_profit_usd": round(self.gross_profit, 2),
            "gross_loss_usd": round(self.gross_loss, 2),
            "profit_factor": round(self.profit_factor, 2) if self.profit_factor != float('inf') else "Inf",
            "average_win_usd": round(self.average_win, 2),
            "average_loss_usd": round(self.average_loss, 2),
            "expectancy_usd": round(self.expectancy, 2),
            "max_consecutive_wins": self.max_consecutive_wins,
            "max_consecutive_losses": self.max_consecutive_losses,
            "return_percent": round(self.return_percent, 2),
            "maximum_drawdown_percent": round(self.maximum_drawdown, 2),
            "maximum_drawdown_usd": round(self.maximum_drawdown_usd, 2),
            "sharpe_ratio": round(self.sharpe_ratio(), 2),
            "sortino_ratio": round(self.sortino_ratio(), 2),
            "cagr_percent": round(self.cagr(), 2),
            "calmar_ratio": round(self.calmar_ratio(), 2) if self.calmar_ratio() != float('inf') else "Inf",
            "recovery_factor": round(self.recovery_factor(), 2) if self.recovery_factor() != float('inf') else "Inf",
        }
    
    def print_summary(self) -> None:
        """Print formatted performance summary to console."""
        summary = self.get_summary()
        
        print("\n" + "="*70)
        print("BACKTEST PERFORMANCE SUMMARY")
        print("="*70)
        print(f"\nTrade Statistics:")
        print(f"  Total Trades:           {summary['total_trades']}")
        print(f"  Winning Trades:         {summary['winning_trades']}")
        print(f"  Losing Trades:          {summary['losing_trades']}")
        print(f"  Win Rate:               {summary['win_rate_percent']}%")
        print(f"  Max Consecutive Wins:   {summary['max_consecutive_wins']}")
        print(f"  Max Consecutive Losses: {summary['max_consecutive_losses']}")
        
        print(f"\nProfitability:")
        print(f"  Total P&L:              ${summary['total_pnl_usd']}")
        print(f"  Gross Profit:           ${summary['gross_profit_usd']}")
        print(f"  Gross Loss:             ${summary['gross_loss_usd']}")
        print(f"  Profit Factor:          {summary['profit_factor']}x")
        print(f"  Average Win:            ${summary['average_win_usd']}")
        print(f"  Average Loss:           ${summary['average_loss_usd']}")
        print(f"  Expectancy:             ${summary['expectancy_usd']}")
        
        print(f"\nRisk Metrics:")
        print(f"  Return:                 {summary['return_percent']}%")
        print(f"  Max Drawdown:           {summary['maximum_drawdown_percent']}%")
        print(f"  Max Drawdown USD:       ${summary['maximum_drawdown_usd']}")
        print(f"  Sharpe Ratio:           {summary['sharpe_ratio']}")
        print(f"  Sortino Ratio:          {summary['sortino_ratio']}")
        print(f"  CAGR:                   {summary['cagr_percent']}%")
        print(f"  Calmar Ratio:           {summary['calmar_ratio']}")
        print(f"  Recovery Factor:        {summary['recovery_factor']}")
        print("\n" + "="*70 + "\n")
