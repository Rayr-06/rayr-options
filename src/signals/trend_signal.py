"""
Trend Signal Engine - Score 0-100
Professional trend detection using multiple indicators
"""
import numpy as np

class TrendSignal:
    """
    Trend Strength Detector
    
    Analyzes:
    - Higher highs / higher lows
    - Moving averages (5/20/50)
    - VWAP position
    - Momentum slope
    
    Output: 0-100 score
    - 0-20: Strong downtrend
    - 20-40: Weak downtrend
    - 40-60: No trend (chop)
    - 60-80: Weak uptrend
    - 80-100: Strong uptrend
    """
    
    def calculate(self, market_snapshot):
        """Calculate trend score from market snapshot"""
        if not market_snapshot or not market_snapshot.get('bars_5m'):
            return 50  # Neutral if no data
        
        bars = market_snapshot['bars_5m']
        current_price = market_snapshot['current_price']
        vwap = market_snapshot['vwap']
        
        if len(bars) < 20:
            return 50
        
        # Score components
        scores = []
        
        # 1. Price vs VWAP (20 points)
        if vwap:
            vwap_score = self._score_vwap_position(current_price, vwap)
            scores.append(vwap_score)
        
        # 2. Moving averages (30 points)
        ma_score = self._score_moving_averages(bars, current_price)
        scores.append(ma_score)
        
        # 3. Higher highs/lows (30 points)
        hh_hl_score = self._score_swing_structure(bars)
        scores.append(hh_hl_score)
        
        # 4. Momentum slope (20 points)
        momentum_score = self._score_momentum(bars)
        scores.append(momentum_score)
        
        # Weighted average
        total_score = sum(scores) / len(scores)
        
        return max(0, min(100, total_score))
    
    def _score_vwap_position(self, price, vwap):
        """Score based on distance from VWAP"""
        distance_pct = (price - vwap) / vwap * 100
        
        if distance_pct > 1.0:
            return 80  # Strong above VWAP
        elif distance_pct > 0.3:
            return 65  # Above VWAP
        elif distance_pct > -0.3:
            return 50  # At VWAP
        elif distance_pct > -1.0:
            return 35  # Below VWAP
        else:
            return 20  # Strong below VWAP
    
    def _score_moving_averages(self, bars, current_price):
        """Score based on MA alignment"""
        closes = [b['close'] for b in bars]
        
        # Calculate MAs
        ma5 = np.mean(closes[-5:]) if len(closes) >= 5 else current_price
        ma20 = np.mean(closes[-20:]) if len(closes) >= 20 else current_price
        
        # Perfect uptrend: Price > MA5 > MA20
        # Perfect downtrend: Price < MA5 < MA20
        
        if current_price > ma5 > ma20:
            return 85  # Strong uptrend
        elif current_price > ma5 and ma5 > ma20 * 0.999:
            return 70  # Uptrend forming
        elif current_price < ma5 < ma20:
            return 15  # Strong downtrend
        elif current_price < ma5 and ma5 < ma20 * 1.001:
            return 30  # Downtrend forming
        else:
            return 50  # Choppy
    
    def _score_swing_structure(self, bars):
        """Score based on swing highs/lows"""
        if len(bars) < 10:
            return 50
        
        highs = [b['high'] for b in bars[-10:]]
        lows = [b['low'] for b in bars[-10:]]
        
        # Count higher highs
        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        
        # Count higher lows
        higher_lows = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])
        
        # Score
        hh_pct = higher_highs / (len(highs) - 1)
        hl_pct = higher_lows / (len(lows) - 1)
        
        avg_pct = (hh_pct + hl_pct) / 2
        
        return avg_pct * 100
    
    def _score_momentum(self, bars):
        """Score based on momentum slope"""
        if len(bars) < 10:
            return 50
        
        closes = [b['close'] for b in bars[-10:]]
        
        # Linear regression slope
        x = list(range(len(closes)))
        slope = np.polyfit(x, closes, 1)[0]
        
        # Normalize slope
        avg_price = np.mean(closes)
        slope_pct = (slope / avg_price) * 100
        
        # Convert to 0-100 score
        if slope_pct > 0.5:
            return 90
        elif slope_pct > 0.2:
            return 70
        elif slope_pct > -0.2:
            return 50
        elif slope_pct > -0.5:
            return 30
        else:
            return 10

if __name__ == "__main__":
    print("Trend Signal Engine - Ready for testing")
