import pandas as pd


def detect_choch(
    df: pd.DataFrame,
    lookback: int = 10
):

    previous_low = (
        df["low"]
        .shift(1)
        .rolling(lookback)
        .min()
    )

    return (
        df["low"] <
        previous_low
    )
