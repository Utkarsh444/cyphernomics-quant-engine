import pandas as pd

from strategy.smc_elliott_strategy import (
    SMCElliottStrategy
)


class Backtester:

    def __init__(self, df):

        self.df = df

        self.trades = []

    def run(self):

        for i in range(
            50,
            len(self.df)
        ):

            sample = (
                self.df.iloc[:i]
            )

            strategy = (
                SMCElliottStrategy(
                    sample
                )
            )

            signal = (
                strategy.signal()
            )

            if signal != "NO_TRADE":

                self.trades.append(
                    {
                        "index": i,
                        "signal": signal,
                        "price":
                        sample["close"]
                        .iloc[-1]
                    }
                )

        return self.trades
