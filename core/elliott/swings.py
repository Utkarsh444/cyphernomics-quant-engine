import pandas as pd


def detect_swings(
    df: pd.DataFrame,
    window: int = 5
):

    highs = (
        df["high"]
        ==
        df["high"]
        .rolling(window, center=True)
        .max()
    )

    lows = (
        df["low"]
        ==
        df["low"]
        .rolling(window, center=True)
        .min()
    )

    return highs, lows
