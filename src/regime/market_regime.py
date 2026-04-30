"""
Market Regime Detector - Professional State Machine
Detects market conditions and adapts strategy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.market_data import MarketDataEngine
from data.vix_data import VIXEngine
import numpy as np

class MarketRegimeDetector:
    """
    Adaptive Market Regime Detection
    
    Regimes:
    - TRENDING_UP: Strong uptrend → Buy calls on pullbacks
    - TRENDING_DOWN: Strong downtrend → Buy puts on bounces
    - RANGING: Choppy/sideways → Sell premium, reduce size
    - HIGH_VOLATILITY: VIX > 25 → Reduce size, faster exits
    - LOW_VOLATILITY: VIX < 15 → Sell premium aggressively
    
    Adapts:
    - Strategy selection
    - Position sizing
    - Stop/target distances
    - Trade frequency
    """
    
    def __init__(self):
        self.market_data = MarketDataEngine()
        self.vix = VIXEngine()
    
    def detect_regime(self):
        """
        Detect current market regime across SPY/QQQ/IWM
        
        Returns:
        {
            'primary_regime': 'TRENDING_UP',
            'confidence': 75,
            'vix_regime': 'NORMAL',
            'spy_regime': {...},
            'qqq_regime': {...},
            'iwm_regime': {...},
            'strategy_guidance': {...}
        }
        """
        # Get VIX state
        vix_state = self.vix.get_vix_state()
        
        # Analyze each symbol
        spy_regime = self._analyze_symbol_regime('SPY')
        qqq_regime = self._analyze_symbol_regime('QQQ')
        iwm_regime = self._analyze_symbol_regime('IWM')
        
        # Determine overall regime
        regimes = [spy_regime, qqq_regime, iwm_regime]
        regimes = [r for r in regimes if r]  # Filter None
        
        if not regimes:
            return self._default_regime()
        
        # Most common regime
        regime_counts = {}
        for r in regimes:
            regime = r['regime']
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        primary_regime = max(regime_counts, key=regime_counts.get)
        confidence = regime_counts[primary_regime] / len(regimes) * 100
        
        # Strategy guidance
        guidance = self._get_strategy_guidance(primary_regime, vix_state)
        
        return {
            'primary_regime': primary_regime,
            'confidence': round(confidence, 1),
            'vix_regime': vix_state['state'],
            'vix_level': vix_state['vix_level'],
            'spy_regime': spy_regime,
            'qqq_regime': qqq_regime,
            'iwm_regime': iwm_regime,
            'strategy_guidance': guidance
        }
    
    def _analyze_symbol_regime(self, symbol):
        """Analyze regime for individual symbol"""
        snapshot = self.market_data.get_market_snapshot(symbol)
        
        if not snapshot or not snapshot.get('bars_5m'):
            return None
        
        bars = snapshot['bars_5m']
        
        if len(bars) < 20:
            return None
        
        # Calculate regime indicators
        trend_strength = self._calculate_trend_strength(bars)
        volatility_level = self._calculate_volatility_level(bars)
        range_tightness = self._calculate_range_tightness(bars)
        
        # Determine regime
        regime = self._classify_regime(trend_strength, volatility_level, range_tightness)
        
        return {
            'symbol': symbol,
            'regime': regime,
            'trend_strength': trend_strength,
            'volatility_level': volatility_level,
            'range_tightness': range_tightness
        }
    
    def _calculate_trend_strength(self, bars):
        """Calculate trend strength (-100 to +100)"""
        closes = [b['close'] for b in bars]
        
        # Linear regression slope
        x = list(range(len(closes)))
        slope = np.polyfit(x, closes, 1)[0]
        
        # Normalize by average price
        avg_price = np.mean(closes)
        trend_pct = (slope / avg_price) * 100 * len(closes)
        
        # Clamp to -100 to +100
        return max(-100, min(100, trend_pct))
    
    def _calculate_volatility_level(self, bars):
        """Calculate volatility level (0-100)"""
        closes = [b['close'] for b in bars]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        
        std_dev = np.std(returns)
        volatility = std_dev * (252 ** 0.5) * 100  # Annualized
        
        # Normalize to 0-100 (assume 50% vol = 100)
        return min(100, volatility * 2)
    
    def _calculate_range_tightness(self, bars):
        """Calculate how tight the range is (0-100)"""
        recent = bars[-10:]
        
        high = max(b['high'] for b in recent)
        low = min(b['low'] for b in recent)
        avg_price = np.mean([b['close'] for b in recent])
        
        range_pct = (high - low) / avg_price * 100
        
        # Tight range (< 2%) = high score
        # Wide range (> 10%) = low score
        if range_pct < 2:
            return 90
        elif range_pct < 4:
            return 70
        elif range_pct < 6:
            return 50
        elif range_pct < 8:
            return 30
        else:
            return 10
    
    def _classify_regime(self, trend_strength, volatility_level, range_tightness):
        """Classify regime based on indicators"""
        
        # Strong trend
        if abs(trend_strength) > 50:
            if trend_strength > 0:
                return 'TRENDING_UP'
            else:
                return 'TRENDING_DOWN'
        
        # High volatility
        if volatility_level > 60:
            return 'HIGH_VOLATILITY'
        
        # Low volatility
        if volatility_level < 25:
            return 'LOW_VOLATILITY'
        
        # Tight range / choppy
        if range_tightness > 60:
            return 'RANGING'
        
        # Default
        return 'NEUTRAL'
    
    def _get_strategy_guidance(self, regime, vix_state):
        """Get strategy guidance for regime"""
        
        guidance = {
            'TRENDING_UP': {
                'preferred_strategy': 'Buy calls on pullbacks',
                'position_size_multiplier': 1.0,
                'stop_distance_multiplier': 1.0,
                'profit_target_multiplier': 1.2,
                'trade_frequency': 'High'
            },
            'TRENDING_DOWN': {
                'preferred_strategy': 'Buy puts on bounces',
                'position_size_multiplier': 1.0,
                'stop_distance_multiplier': 1.0,
                'profit_target_multiplier': 1.2,
                'trade_frequency': 'High'
            },
            'RANGING': {
                'preferred_strategy': 'Sell premium (iron condors)',
                'position_size_multiplier': 0.8,
                'stop_distance_multiplier': 0.8,
                'profit_target_multiplier': 0.8,
                'trade_frequency': 'Low'
            },
            'HIGH_VOLATILITY': {
                'preferred_strategy': 'Reduce size, faster exits',
                'position_size_multiplier': 0.5,
                'stop_distance_multiplier': 1.5,
                'profit_target_multiplier': 0.8,
                'trade_frequency': 'Very Low'
            },
            'LOW_VOLATILITY': {
                'preferred_strategy': 'Sell premium aggressively',
                'position_size_multiplier': 1.2,
                'stop_distance_multiplier': 1.0,
                'profit_target_multiplier': 1.0,
                'trade_frequency': 'High'
            },
            'NEUTRAL': {
                'preferred_strategy': 'Selective trades only',
                'position_size_multiplier': 0.7,
                'stop_distance_multiplier': 1.0,
                'profit_target_multiplier': 1.0,
                'trade_frequency': 'Medium'
            }
        }
        
        base_guidance = guidance.get(regime, guidance['NEUTRAL'])
        
        # Adjust for VIX
        if vix_state['state'] == 'FEAR':
            base_guidance['position_size_multiplier'] *= 0.5
            base_guidance['trade_frequency'] = 'Very Low'
        
        return base_guidance
    
    def _default_regime(self):
        """Default regime when data unavailable"""
        return {
            'primary_regime': 'NEUTRAL',
            'confidence': 0,
            'vix_regime': 'NORMAL',
            'vix_level': 15,
            'strategy_guidance': {
                'preferred_strategy': 'Wait for clear signal',
                'position_size_multiplier': 0.5,
                'trade_frequency': 'Very Low'
            }
        }

if __name__ == "__main__":
    print("\n" + "="*100)
    print("MARKET REGIME DETECTOR TEST")
    print("="*100)
    
    detector = MarketRegimeDetector()
    regime = detector.detect_regime()
    
    print(f"\nPrimary Regime: {regime['primary_regime']} (Confidence: {regime['confidence']}%)")
    print(f"VIX Regime: {regime['vix_regime']} ({regime['vix_level']:.2f})")
    
    print("\nStrategy Guidance:")
    for key, value in regime['strategy_guidance'].items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*100 + "\n")
