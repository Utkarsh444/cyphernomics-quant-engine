from core.smc.bos import detect_bos
from core.smc.choch import detect_choch
from core.smc.fvg import detect_fvg
from core.smc.order_blocks import (
    detect_order_blocks
)

from core.elliott.wave_counter import (
    WaveCounter
)

from core.elliott.validator import (
    ElliottValidator
)


class SMCElliottStrategy:

    def __init__(self, df):

        self.df = df

    def signal(self):

        bos = detect_bos(self.df)

        choch = detect_choch(
            self.df
        )

        bull_fvg, bear_fvg = (
            detect_fvg(
                self.df
            )
        )

        bull_ob, bear_ob = (
            detect_order_blocks(
                self.df
            )
        )

        wave_counter = (
            WaveCounter(
                self.df
            )
        )

        wave = (
            wave_counter.count()
        )

        valid_wave = (
            ElliottValidator
            .validate(
                wave["wave_count"]
            )
            if wave
            else False
        )

        latest = self.df.index[-1]

        if (
            bos.loc[latest]
            and bull_fvg.loc[latest]
            and bull_ob.loc[latest]
            and valid_wave
        ):
            return "BUY"

        if (
            choch.loc[latest]
            and bear_fvg.loc[latest]
            and bear_ob.loc[latest]
            and valid_wave
        ):
            return "SELL"

        return "NO_TRADE"
