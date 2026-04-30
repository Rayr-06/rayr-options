"""
Composite Score Calculator - Master Signal Aggregator
Combines all signals into a single confidence score 0-100
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from signals.trend_signal import TrendSignal
from signals.mean_reversion import MeanReversionSignal
from signals.volatility_signal import VolatilitySignal
from data.market_data import MarketDataEngine
from data.vix_data import VIXEngine

class CompositeScoreCalculator:
    """
    Master Signal Aggregator
    
    Combines:
    - Trend (35% weight)
    - Mean Reversion (25% weight)
    - Volatility (25% weight)
    - VIX State (15% weight)
    
    Output:
    - confidence: 0-100 overall score
    - direction: CALL/PUT/NEUTRAL
    - signals: Individual signal breakdown
    - recommendation: Trade or no trade
    """
    
    def __init__(self):
        self.trend = TrendSignal()
        self.mean_reversion = MeanReversionSignal()
        self.volatility = VolatilitySignal()
        self.market_data = MarketDataEngine()
        self.vix = VIXEngine()
        
        # Weights
        self.weights = {
            'trend': 0.35,
            'mean_reversion': 0.25,
            'volatility': 0.25,
            'vix': 0.15
        }
    
    def calculate_for_symbol(self, symbol):
        """
        Calculate composite score for a symbol
        
        Returns:
        {
            'symbol': 'SPY',
            'confidence': 75.5,
            'direction': 'CALL',
            'signals': {
                'trend': 80,
                'mean_reversion': 60,
                'volatility': 70,
                'vix': 85
            },
            'vix_state': {...},
            'recommendation': 'STRONG BUY',
            'trade_type': 'TREND_FOLLOWING',
            'market_snapshot': {...}
        }
        """
        # Get market snapshot
        snapshot = self.market_data.get_market_snapshot(symbol)
        
        if not snapshot:
            return None
        
        # Get VIX state
        vix_state = self.vix.get_vix_state()
        
        # Calculate individual signals
        trend_score = self.trend.calculate(snapshot)
        mr_score = self.mean_reversion.calculate(snapshot)
        vol_score = self.volatility.calculate(snapshot)
        
        # VIX score (convert state to 0-100)
        vix_score = self._vix_state_to_score(vix_state)
        
        # Weighted composite
        composite = (
            trend_score * self.weights['trend'] +
            mr_score * self.weights['mean_reversion'] +
            vol_score * self.weights['volatility'] +
            vix_score * self.weights['vix']
        )
        
        # Determine direction
        direction = self._determine_direction(
            trend_score, 
            mr_score, 
            composite
        )
        
        # Determine trade type
        trade_type = self._determine_trade_type(
            trend_score,
            mr_score,
            vol_score,
            vix_state
        )
        
        # Recommendation
        recommendation = self._get_recommendation(
            composite,
            vix_state,
            direction
        )
        
        return {
            'symbol': symbol,
            'confidence': round(composite, 2),
            'direction': direction,
            'signals': {
                'trend': round(trend_score, 2),
                'mean_reversion': round(mr_score, 2),
                'volatility': round(vol_score, 2),
                'vix': round(vix_score, 2)
            },
            'vix_state': vix_state,
            'recommendation': recommendation,
            'trade_type': trade_type,
            'market_snapshot': snapshot
        }
    
    def _vix_state_to_score(self, vix_state):
        """Convert VIX state to 0-100 score"""
        # Higher score = better for trading
        state_scores = {
            'COMPLACENT': 90,  # Best for selling premium
            'NORMAL': 70,      # Good for most trades
            'ELEVATED': 50,    # Caution
            'FEAR': 20         # Avoid premium selling
        }
        return state_scores.get(vix_state['state'], 50)
    
    def _determine_direction(self, trend_score, mr_score, composite):
        """Determine CALL/PUT/NEUTRAL"""
        
        # Strong trend dominates
        if trend_score > 70:
            return 'CALL'
        elif trend_score < 30:
            return 'PUT'
        
        # Mean reversion in choppy market
        if 40 <= trend_score <= 60:
            if mr_score > 70:
                return 'PUT'  # Overbought, fade it
            elif mr_score < 30:
                return 'CALL'  # Oversold, buy it
        
        # Composite decides
        if composite > 60:
            return 'CALL'
        elif composite < 40:
            return 'PUT'
        else:
            return 'NEUTRAL'
    
    def _determine_trade_type(self, trend_score, mr_score, vol_score, vix_state):
        """Determine best strategy type"""
        
        # Premium selling (low VIX, high vol score)
        if vix_state['state'] in ['COMPLACENT', 'NORMAL'] and vol_score > 60:
            return 'PREMIUM_SELLING'
        
        # Trend following (strong trend)
        if trend_score > 70 or trend_score < 30:
            return 'TREND_FOLLOWING'
        
        # Mean reversion (extreme MR score)
        if mr_score > 75 or mr_score < 25:
            return 'MEAN_REVERSION'
        
        # Volatility expansion (compressed, low vol)
        if vol_score < 30:
            return 'VOLATILITY_EXPANSION'
        
        return 'NO_CLEAR_EDGE'
    
    def _get_recommendation(self, composite, vix_state, direction):
        """Get trading recommendation"""
        
        # VIX check
        if not vix_state['allow_premium_selling']:
            if composite < 80:  # Need very strong signal in high VIX
                return 'NO TRADE - VIX TOO HIGH'
        
        # Confidence thresholds
        if composite >= 80:
            return f'STRONG {direction}'
        elif composite >= 70:
            return f'MODERATE {direction}'
        elif composite >= 60:
            return f'WEAK {direction}'
        else:
            return 'NO TRADE - LOW CONFIDENCE'
    
    def scan_all_symbols(self):
        """Scan SPY, QQQ, IWM and return best opportunity"""
        results = []
        
        for symbol in ['SPY', 'QQQ', 'IWM']:
            score = self.calculate_for_symbol(symbol)
            if score:
                results.append(score)
        
        if not results:
            return None
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'best_opportunity': results[0],
            'all_results': results
        }

if __name__ == "__main__":
    print("\n" + "="*100)
    print("COMPOSITE SCORE CALCULATOR TEST")
    print("="*100)
    
    calc = CompositeScoreCalculator()
    scan_results = calc.scan_all_symbols()
    
    if scan_results:
        print("\nBEST OPPORTUNITY:")
        best = scan_results['best_opportunity']
        print(f"\nSymbol: {best['symbol']}")
        print(f"Confidence: {best['confidence']}/100")
        print(f"Direction: {best['direction']}")
        print(f"Trade Type: {best['trade_type']}")
        print(f"Recommendation: {best['recommendation']}")
        
        print("\nSignal Breakdown:")
        for signal, score in best['signals'].items():
            print(f"  {signal}: {score}/100")
        
        print(f"\nVIX State: {best['vix_state']['state']} ({best['vix_state']['vix_level']:.2f})")
        
        print("\n" + "="*100)
        
        print("\nALL OPPORTUNITIES:")
        for result in scan_results['all_results']:
            print(f"  {result['symbol']}: {result['confidence']:.1f}/100 - {result['recommendation']}")
    
    print("\n" + "="*100 + "\n")
