"""
Mean Reversion Signal - Score 0-100
Detects overbought/oversold conditions
"""
import numpy as np

class MeanReversionSignal:
    """
    Mean Reversion Detector
    
    Analyzes:
    - RSI (14-period)
    - Bollinger Bands (20-period, 2 std dev)
    - Distance from moving average
    - Recent price extremes
    
    Output: 0-100 score
    - 0-20: Extremely oversold (buy signal)
    - 20-40: Oversold
    - 40-60: Neutral
    - 60-80: Overbought
    - 80-100: Extremely overbought (sell signal)
    """
    
    def calculate(self, market_snapshot):
        """Calculate mean reversion score"""
        if not market_snapshot or not market_snapshot.get('bars_5m'):
            return 50
        
        bars = market_snapshot['bars_5m']
        current_price = market_snapshot['current_price']
        
        if len(bars) < 20:
            return 50
        
        scores = []
        
        # 1. RSI (40 points)
        rsi_score = self._score_rsi(bars, current_price)
        scores.append(rsi_score)
        
        # 2. Bollinger Bands (40 points)
        bb_score = self._score_bollinger_bands(bars, current_price)
        scores.append(bb_score)
        
        # 3. Recent extremes (20 points)
        extreme_score = self._score_recent_extremes(bars, current_price)
        scores.append(extreme_score)
        
        return sum(scores) / len(scores)
    
    def _score_rsi(self, bars, current_price):
        """Calculate RSI-based score"""
        closes = [b['close'] for b in bars]
        
        # Calculate RSI
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Convert RSI to our 0-100 scale
        # RSI 30 = oversold (score 20)
        # RSI 50 = neutral (score 50)
        # RSI 70 = overbought (score 80)
        
        if rsi < 30:
            return 20  # Oversold
        elif rsi < 40:
            return 35
        elif rsi < 60:
            return 50
        elif rsi < 70:
            return 65
        else:
            return 80  # Overbought
    
    def _score_bollinger_bands(self, bars, current_price):
        """Score based on Bollinger Band position"""
        closes = [b['close'] for b in bars]
        
        # Calculate 20-period MA and std dev
        ma20 = np.mean(closes[-20:])
        std20 = np.std(closes[-20:])
        
        # Bollinger Bands
        upper_band = ma20 + (2 * std20)
        lower_band = ma20 - (2 * std20)
        
        # Position within bands
        if current_price >= upper_band:
            return 90  # At/above upper band (overbought)
        elif current_price >= ma20 + std20:
            return 70  # Upper half
        elif current_price >= ma20:
            return 55  # Above middle
        elif current_price >= ma20 - std20:
            return 45  # Below middle
        elif current_price >= lower_band:
            return 30  # Lower half
        else:
            return 10  # At/below lower band (oversold)
    
    def _score_recent_extremes(self, bars, current_price):
        """Score based on recent price extremes"""
        recent = bars[-10:]
        
        high = max(b['high'] for b in recent)
        low = min(b['low'] for b in recent)
        
        if high == low:
            return 50
        
        # Position in recent range (0-1)
        position = (current_price - low) / (high - low)
        
        # Convert to 0-100 score
        return position * 100

if __name__ == "__main__":
    print("Mean Reversion Signal Engine - Ready")
