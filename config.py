from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"

RISK_PER_TRADE = 0.02
DAILY_MAX_LOSS = 0.03
RR_RATIO = 
