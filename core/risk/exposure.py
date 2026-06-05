class ExposureManager:

    def __init__(
        self,
        max_portfolio_risk=0.06
    ):
        self.max_portfolio_risk = (
            max_portfolio_risk
        )

    def can_open_trade(
        self,
        current_risk,
        proposed_risk
    ):

        return (
            current_risk +
            proposed_risk
        ) <= self.max_portfolio_risk
