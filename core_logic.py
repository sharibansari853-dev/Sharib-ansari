# core_logic.py
# Trading data fetch + indicator calculations.
# Kept separate from UI so logic can be tested independently.

import urllib.request
import urllib.error
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
}


def get_live_data(ticker):
    """
    Fetch closing prices for a ticker.
    Tries Yahoo Finance first, falls back to Stooq.
    Returns (prices_list, error_message). error_message is None on success.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=60d&interval=1d"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            result = data['chart']['result'][0]
            prices = result['indicators']['quote'][0]['close']
            cleaned_prices = [p for p in prices if p is not None]
            if len(cleaned_prices) >= 20:
                return cleaned_prices, None
    except urllib.error.HTTPError as e:
        yahoo_error = f"Yahoo Finance error (HTTP {e.code}). Trying Stooq..."
    except urllib.error.URLError as e:
        yahoo_error = f"Network problem: {e.reason}. Trying Stooq..."
    except Exception as e:
        yahoo_error = f"Yahoo parse error: {e}. Trying Stooq..."
    else:
        yahoo_error = "Not enough data points from Yahoo. Trying Stooq..."

    stooq_symbol = _to_stooq_symbol(ticker)
    stooq_url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
    try:
        req = urllib.request.Request(stooq_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode()
            lines = [line for line in text.strip().split("\n") if line]
            if len(lines) < 21 or "Date" not in lines[0]:
                return [], f"{yahoo_error}\nStooq: symbol galat hai ya data nahi mila."
            closes = []
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) >= 5:
                    try:
                        closes.append(float(parts[4]))
                    except ValueError:
                        continue
            if len(closes) >= 20:
                return closes, None
            return [], f"{yahoo_error}\nStooq: kaafi data points nahi mile."
    except urllib.error.HTTPError as e:
        return [], f"{yahoo_error}\nStooq HTTP {e.code} error."
    except urllib.error.URLError as e:
        return [], f"{yahoo_error}\nInternet connection check karein: {e.reason}"
    except Exception as e:
        return [], f"{yahoo_error}\nStooq error: {e}"


def _to_stooq_symbol(ticker):
    t = ticker.upper()
    if t.endswith(".NS"):
        return t.replace(".NS", "").lower() + ".in"
    if t.endswith("=X"):
        base = t.replace("=X", "")
        if len(base) == 3:
            return ("usd" + base).lower()
        return base.lower()
    if t.startswith("^"):
        return t.lower()
    return t.lower()


def calculate_indicators(prices):
    current_price = prices[-1]
    sma_20 = sum(prices[-20:]) / 20

    period = min(14, len(prices) - 1)
    if period < 1:
        return current_price, sma_20, 50.0

    gains = 0
    losses = 0
    for i in range(len(prices) - period, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        rsi = 100.0
    elif gains == 0:
        rsi = 0.0
    else:
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))

    return current_price, sma_20, rsi


def get_signal(current_price, sma_20, rsi, is_forex=False):
    """
    Returns (signal_text, color_name, reason_text)
    color_name is one of: 'green', 'red', 'grey'
    """
    if current_price > sma_20 and rsi < 65:
        reason = ("Currency me strong momentum hai aur trend upar hai."
                   if is_forex else
                   "Stock me buying pressure hai, up-trend confirm hai.")
        return "INVEST / BUY", "green", reason

    elif rsi > 70:
        return "AVOID / DANGER", "red", "Yeh bohot mehenga (Overbought) ho chuka hai, gir sakta hai!"

    elif current_price < sma_20:
        return "DO NOT BUY / SELL", "red", "Price down-trend mein ja raha hai."

    else:
        return "HOLD / WAIT", "grey", "Market stable hai, clear confirmation ka wait karein."


def analyze(ticker, is_forex=False):
    """
    High-level function the UI calls. Returns a dict with all results,
    or a dict with 'error' key set if something failed.
    """
    prices, error = get_live_data(ticker)
    if error:
        return {"error": error}
    if not prices or len(prices) < 20:
        return {"error": "Data nahi mil saka ya symbol galat hai. Kripya check karein."}

    current_price, sma_20, rsi = calculate_indicators(prices)
    signal, color, reason = get_signal(current_price, sma_20, rsi, is_forex)

    return {
        "ticker": ticker,
        "current_price": current_price,
        "sma_20": sma_20,
        "rsi": rsi,
        "signal": signal,
        "color": color,
        "reason": reason,
    }
