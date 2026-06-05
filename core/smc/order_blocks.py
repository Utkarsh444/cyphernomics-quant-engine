import pandas as pd


def detect_order_blocks(
    df: pd.DataFrame
):

    bullish_ob = (
        (
            df["close"].shift(1)
            <
            df["open"].shift(1)
        )
        &
        (
            df["close"]
            >
            df["high"].shift(1)
        )
    )

    bearish_ob = (
        (
            df["close"].shift(1)
            >
            df["open"].shift(1)
        )
        &
        (
            df["close"]
            <
            df["low"].shift(1)
        )
    )

    return (
        bullish_ob,
        bearish_ob
    )
