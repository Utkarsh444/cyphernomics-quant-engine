from dataclasses import dataclass


@dataclass
class TradeRisk:
    account_balance: float
    risk_percent: float = 0.02

    def position_size(
        self,
        entry_price: float,
        stop_price: float
    ) -> float:

        risk_amount = (
            self.account_balance *
            self.risk_percent
        )

        stop_distance = abs(
            entry_price -
            stop_price
        )

        if stop_distance <= 0:
            raise ValueError(
                "Invalid stop distance"
            )

        return (
            risk_amount /
            stop_distance
        )
