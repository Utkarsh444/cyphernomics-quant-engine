import pandas as pd

from core.elliott.swings import (
    detect_swings
)


def build_zigzag(
    df: pd.DataFrame,
    window: int = 5
):

    swing_highs, swing_lows = (
        detect_swings(
            df,
            window
        )
    )

    pivots = []

    for idx in df.index:

        if swing_highs.loc[idx]:

            pivots.append(
                (
                    idx,
                    "HIGH",
                    df.loc[idx, "high"]
                )
            )

        elif swing_lows.loc[idx]:

            pivots.append(
                (
                    idx,
                    "LOW",
                    df.loc[idx, "low"]
                )
            )

    return pivots
