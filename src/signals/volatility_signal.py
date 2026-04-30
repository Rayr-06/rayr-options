"""
Volatility Signal Engine - Score 0-100
Detects volatility expansion/contraction opportunities
"""
import numpy as np

class VolatilitySignal:
    """
    Volatility Opportunity Detector
    
    Key Insight: 
    - High IV = Sell premium (options expensive)
    - Low IV = Buy options (options cheap, potential expansion)
    
    Analyzes:
    - ATR vs historical ATR
    - Price range compression
    - Volume spikes
    - Recent volatility trend
    
    Output: 0-100 score
    - 0-20: Extremely low volatility (buy options)
    - 20-40: Low volatility (neutral to buy)
    - 40-60: Normal volatility
    - 60-80: High volatility (sell premium)
    - 80-100: Extremely high volatility (strong sell premium)
    """
    
    def calculate(self, market_snapshot):
        """Calculate volatility signal score"""
        if not market_snapshot or not market_snapshot.get('bars_5m'):
            return 50
        
        bars = market_snapshot['bars_5m']
        current_atr = market_snapshot.get('atr', 0)
        
        if len(bars) < 20 or not current_atr:
            return 50
        
        scores = []
        
        # 1. ATR percentile (40 points)
        atr_score = self._score_atr_percentile(bars, current_atr)
        scores.append(atr_score)
        
        # 2. Price range compression (30 points)
        compression_score = self._score_range_compression(bars)
        scores.append(compression_score)
        
        # 3. Volume spike (30 points)
        volume_score = self._score_volume_spike(bars)
        scores.append(volume_score)
        
        return sum(scores) / len(scores)
    
    def _score_atr_percentile(self, bars, current_atr):
        """Score ATR vs historical ATR"""
        # Calculate ATR for each period
        atrs = []
        for i in range(1, len(bars)):
            high = bars[i]['high']
            low = bars[i]['low']
            prev_close = bars[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            atrs.append(tr)
        
        if len(atrs) < 10:
            return 50
        
        # Calculate percentile
        percentile = sum(1 for atr in atrs if atr <= current_atr) / len(atrs) * 100
        
        # High percentile = high volatility = good for selling premium
        return percentile
    
    def _score_range_compression(self, bars):
        """Detect range compression (precursor to expansion)"""
        if len(bars) < 10:
            return 50
        
        recent = bars[-5:]
        older = bars[-10:-5]
        
        # Average range for recent vs older
        recent_avg_range = np.mean([b['high'] - b['low'] for b in recent])
        older_avg_range = np.mean([b['high'] - b['low'] for b in older])
        
        if older_avg_range == 0:
            return 50
        
        # Compression ratio
        ratio = recent_avg_range / older_avg_range
        
        # Strong compression (ratio < 0.7) suggests expansion coming
        # Score inversely - compression = low volatility score
        if ratio < 0.6:
            return 20  # Very compressed (volatility likely to expand)
        elif ratio < 0.8:
            return 35  # Compressed
        elif ratio < 1.2:
            return 50  # Normal
        elif ratio < 1.5:
            return 65  # Expanding
        else:
            return 80  # Strong expansion
    
    def _score_volume_spike(self, bars):
        """Detect volume spikes (indicates volatility)"""
        if len(bars) < 10:
            return 50
        
        recent_volume = bars[-1]['volume']
        avg_volume = np.mean([b['volume'] for b in bars[-10:]])
        
        if avg_volume == 0:
            return 50
        
        volume_ratio = recent_volume / avg_volume
        
        # High volume = high volatility
        if volume_ratio > 3.0:
            return 90
        elif volume_ratio > 2.0:
            return 75
        elif volume_ratio > 1.5:
            return 60
        elif volume_ratio > 0.7:
            return 50
        else:
            return 35

if __name__ == "__main__":
    print("Volatility Signal Engine - Ready")
