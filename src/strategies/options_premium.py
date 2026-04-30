"""
STRATEGY 1: OPTIONS PREMIUM SELLING
Primary money-maker - automated weekly put selling
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.options_engine import OptionsEngine

class OptionsPremiumStrategy:
    def __init__(self, broker):
        self.name = "OPTIONS_PREMIUM"
        self.broker = broker
        self.engine = OptionsEngine()
        
        # IV estimates (historical averages)
        self.iv_estimates = {
            'SPY': 0.15,
            'QQQ': 0.20,
            'IWM': 0.22
        }
    
    def scan(self):
        """Scan for weekly put opportunities"""
        symbols = ['SPY', 'QQQ', 'IWM']
        opportunities = []
        
        for symbol in symbols:
            try:
                quote = self.broker.get_quote(symbol)
                if not quote:
                    continue
                
                S = quote['mid']
                iv = self.iv_estimates.get(symbol, 0.20)
                T = 7 / 365
                
                K = self.engine.find_strike_for_delta(S, 0.30, T, 0.05, iv, 'put')
                premium = self.engine.black_scholes_price(S, K, T, 0.05, iv, 'put')
                
                return_pct = (premium / K) * 100
                
                if return_pct >= 0.3:
                    opportunities.append({
                        'symbol': symbol,
                        'current_price': S,
                        'strike': round(K, 2),
                        'premium': round(premium, 2),
                        'return_pct': return_pct,
                        'annual_return': return_pct * 52,
                        'iv': iv,
                        'expiry': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                    })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        opportunities.sort(key=lambda x: x['return_pct'], reverse=True)
        return opportunities
