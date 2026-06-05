import pandas as pd


def detect_fvg(
    df: pd.DataFrame
):

    bullish = (
        df["low"].shift(-1)
        >
        df["high"].shift(1)
    )

    bearish = (
        df["high"].shift(-1)
        <
        df["low"].shift(1)
    )

    return bullish, bearish
