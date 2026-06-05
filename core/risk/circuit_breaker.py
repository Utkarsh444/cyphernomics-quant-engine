class DailyLossCircuitBreaker:

    def __init__(
        self,
        start_balance,
        max_loss=0.03
    ):

        self.start_balance = (
            start_balance
        )

        self.max_loss = max_loss

    def triggered(
        self,
        current_equity
    ):

        loss_pct = (
            self.start_balance -
            current_equity
        ) / self.start_balance

        return (
            loss_pct >=
            self.max_loss
        )
