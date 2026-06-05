from core.smc.bos import detect_bos
from core.smc.choch import detect_choch


def detect_mss(df):

    bos = detect_bos(df)
    choch = detect_choch(df)

    return (
        bos |
        choch
    )
