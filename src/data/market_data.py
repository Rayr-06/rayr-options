"""
Market Data Engine - Professional Grade
Fetches real-time market data with multiple fallbacks
"""
import os
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import numpy as np

class MarketDataEngine:
    """
    Fetches and processes market data for SPY, QQQ, IWM
    
    Features:
    - Real-time quotes
    - Historical bars (1m, 5m, 15m)
    - VWAP calculation
    - ATR calculation
    - Volume analysis
    """
    
    def __init__(self):
        self.client = StockHistoricalDataClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY')
        )
        self.symbols = ['SPY', 'QQQ', 'IWM']
    
    def get_latest_quotes(self):
        """Get current prices for all symbols"""
        request = StockLatestQuoteRequest(symbol_or_symbols=self.symbols)
        quotes = self.client.get_stock_latest_quote(request)
        
        return {
            symbol: {
                'bid': float(quote.bid_price),
                'ask': float(quote.ask_price),
                'mid': (float(quote.bid_price) + float(quote.ask_price)) / 2,
                'spread': float(quote.ask_price) - float(quote.bid_price),
                'timestamp': quote.timestamp
            }
            for symbol, quote in quotes.items()
        }
    
    def get_intraday_bars(self, symbol, timeframe='5Min', limit=100):
        """
        Get intraday bars for technical analysis
        
        Returns bars with:
        - open, high, low, close
        - volume
        - vwap
        - trade_count
        """
        tf_map = {
            '1Min': TimeFrame.Minute,
            '5Min': TimeFrame(5, TimeFrame.Minute),
            '15Min': TimeFrame(15, TimeFrame.Minute)
        }
        
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf_map.get(timeframe, TimeFrame(5, TimeFrame.Minute)),
            start=datetime.now() - timedelta(days=1),
            limit=limit
        )
        
        bars = self.client.get_stock_bars(request)
        
        if symbol not in bars:
            return None
        
        data = []
        for bar in bars[symbol]:
            data.append({
                'timestamp': bar.timestamp,
                'open': float(bar.open),
                'high': float(bar.high),
                'low': float(bar.low),
                'close': float(bar.close),
                'volume': int(bar.volume),
                'vwap': float(bar.vwap) if bar.vwap else None,
                'trade_count': int(bar.trade_count) if bar.trade_count else None
            })
        
        return data
    
    def calculate_vwap(self, bars):
        """Calculate VWAP from bars"""
        if not bars:
            return None
        
        total_volume = sum(b['volume'] for b in bars)
        if total_volume == 0:
            return None
        
        vwap = sum(b['close'] * b['volume'] for b in bars) / total_volume
        return vwap
    
    def calculate_atr(self, bars, period=14):
        """Calculate Average True Range"""
        if not bars or len(bars) < period:
            return None
        
        true_ranges = []
        for i in range(1, len(bars)):
            high = bars[i]['high']
            low = bars[i]['low']
            prev_close = bars[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        atr = np.mean(true_ranges[-period:])
        return atr
    
    def get_market_snapshot(self, symbol):
        """
        Get comprehensive market snapshot for a symbol
        
        Returns:
        - Current price
        - VWAP
        - ATR
        - Relative volume
        - Price vs VWAP
        """
        # Get current quote
        quotes = self.get_latest_quotes()
        current_price = quotes[symbol]['mid']
        
        # Get intraday bars
        bars_5m = self.get_intraday_bars(symbol, '5Min', 100)
        
        if not bars_5m:
            return None
        
        # Calculate metrics
        vwap = self.calculate_vwap(bars_5m)
        atr = self.calculate_atr(bars_5m)
        
        # Volume analysis
        recent_volume = sum(b['volume'] for b in bars_5m[-10:])  # Last 50 min
        avg_volume = sum(b['volume'] for b in bars_5m) / len(bars_5m)
        relative_volume = recent_volume / (avg_volume * 10) if avg_volume > 0 else 1.0
        
        # Price vs VWAP
        vwap_distance = ((current_price - vwap) / vwap * 100) if vwap else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'vwap': vwap,
            'atr': atr,
            'relative_volume': relative_volume,
            'vwap_distance_pct': vwap_distance,
            'above_vwap': current_price > vwap if vwap else None,
            'bars_5m': bars_5m[-20:],  # Last 20 bars for analysis
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    engine = MarketDataEngine()
    
    print("\n" + "="*100)
    print("MARKET DATA ENGINE TEST")
    print("="*100)
    
    for symbol in ['SPY', 'QQQ', 'IWM']:
        snapshot = engine.get_market_snapshot(symbol)
        
        if snapshot:
            print(f"\n{symbol}:")
            print(f"  Price: ${snapshot['current_price']:.2f}")
            print(f"  VWAP: ${snapshot['vwap']:.2f} ({snapshot['vwap_distance_pct']:+.2f}%)")
            print(f"  ATR: ${snapshot['atr']:.2f}")
            print(f"  Rel Volume: {snapshot['relative_volume']:.2f}x")
    
    print("\n" + "="*100 + "\n")
