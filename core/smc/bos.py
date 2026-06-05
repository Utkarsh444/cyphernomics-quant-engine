import pandas as pd


def detect_bos(df: pd.DataFrame, lookback: int = 10):

    previous_high = (
        df["high"]
        .shift(1)
        .rolling(lookback)
        .max()
    )

    return (
        df["high"] >
        previous_high
    )
