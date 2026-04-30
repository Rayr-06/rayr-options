"""
Market Data Engine - Real-time market data via Alpaca
"""
import os
import numpy as np
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

class MarketDataEngine:
    """
    Fetches live market data for SPY, QQQ, IWM
    - Latest quotes
    - Intraday bars
    - VWAP calculation
    - ATR calculation
    - Volume analysis
    """

    def __init__(self):
        # Load API keys from environment
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError('ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env')
        
        self.client = StockHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key
        )
        self.symbols = ['SPY', 'QQQ', 'IWM']

    def get_latest_quotes(self):
        """Get current prices for all symbols"""
        request = StockLatestQuoteRequest(symbol_or_symbols=self.symbols)
        quotes = self.client.get_stock_latest_quote(request)
        
        result = {}
        for symbol in self.symbols:
            q = quotes[symbol]
            result[symbol] = {
                'bid': float(q.bid_price),
                'ask': float(q.ask_price),
                'mid': (float(q.bid_price) + float(q.ask_price)) / 2,
                'timestamp': q.timestamp
            }
        return result

    def get_intraday_bars(self, symbol, timeframe='5Min', limit=100):
        """Get intraday bars for a symbol"""
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame(5, TimeFrame.Minute) if timeframe == '5Min' else TimeFrame(1, TimeFrame.Minute),
            limit=limit
        )
        
        bars = self.client.get_stock_bars(request)
        
        result = []
        for bar in bars[symbol]:
            result.append({
                'timestamp': bar.timestamp,
                'open': float(bar.open),
                'high': float(bar.high),
                'low': float(bar.low),
                'close': float(bar.close),
                'volume': int(bar.volume),
                'vwap': float(bar.vwap) if hasattr(bar, 'vwap') and bar.vwap else float(bar.close)
            })
        
        return result

    def calculate_vwap(self, bars):
        """Calculate VWAP from bars"""
        if not bars:
            return None
        
        total_volume = sum(b['volume'] for b in bars)
        if total_volume == 0:
            return bars[-1]['close']
        
        vwap = sum(b['vwap'] * b['volume'] for b in bars) / total_volume
        return vwap

    def calculate_atr(self, bars, period=14):
        """Calculate Average True Range"""
        if len(bars) < period + 1:
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
        
        if len(true_ranges) < period:
            return None
        
        atr = np.mean(true_ranges[-period:])
        return atr

    def get_market_snapshot(self, symbol):
        """Get complete market snapshot for a symbol"""
        try:
            # Get latest quote
            quotes = self.get_latest_quotes()
            current_price = quotes[symbol]['mid']
            
            # Get recent bars
            bars = self.get_intraday_bars(symbol, timeframe='5Min', limit=100)
            
            if not bars:
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'vwap': current_price,
                    'atr': 0,
                    'error': 'No bars available'
                }
            
            # Calculate metrics
            vwap = self.calculate_vwap(bars)
            atr = self.calculate_atr(bars)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'vwap': vwap if vwap else current_price,
                'atr': atr if atr else 0,
                'bars_count': len(bars),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'current_price': 0,
                'vwap': 0,
                'atr': 0
            }
