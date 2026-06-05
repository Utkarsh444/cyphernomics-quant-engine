from core.elliott.zigzag import (
    build_zigzag
)


class WaveCounter:

    def __init__(self, df):

        self.df = df

    def count(self):

        pivots = build_zigzag(
            self.df
        )

        if len(pivots) < 5:

            return None

        return {
            "wave_count":
            len(pivots)
        }
