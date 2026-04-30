"""
Kelly Criterion Position Sizer - Professional Money Management
The mathematical secret to long-term compounding
"""
import json
import os

class KellyPositionSizer:
    """
    Kelly Criterion Position Sizing
    
    Formula: f = (p*b - q) / b
    Where:
    - f = fraction of capital to risk
    - p = probability of winning
    - q = probability of losing (1-p)
    - b = win/loss ratio
    
    Safety Features:
    - Half Kelly (divide by 2 for safety)
    - Max position cap (never risk > 3% per trade)
    - Min position floor (at least $10 to make trade worthwhile)
    - Account size scaling
    
    For $500 account:
    - A+ setup (80+ confidence): ~$15 risk
    - B setup (70-79 confidence): ~$12 risk
    - C setup (60-69 confidence): ~$10 risk
    - < 60 confidence: NO TRADE
    """
    
    def __init__(self, account_size=500, max_risk_pct=3.0):
        self.account_size = account_size
        self.max_risk_pct = max_risk_pct
        self.max_risk_usd = account_size * (max_risk_pct / 100)
        
        # Historical performance (will be updated from analytics)
        self.historical_stats = self._load_historical_stats()
    
    def _load_historical_stats(self):
        """Load historical trading stats for Kelly calculation"""
        try:
            if os.path.exists('data/analytics.json'):
                with open('data/analytics.json', 'r') as f:
                    analytics = json.load(f)
                    
                    tm = analytics.get('trade_metrics', {})
                    
                    return {
                        'win_rate': tm.get('win_rate', 50) / 100,  # Convert to decimal
                        'avg_winner': tm.get('avg_winner', 20),
                        'avg_loser': tm.get('avg_loser', 15),
                        'total_trades': analytics.get('total_trades', 0)
                    }
        except:
            pass
        
        # Conservative defaults until we have history
        return {
            'win_rate': 0.50,  # 50%
            'avg_winner': 20,
            'avg_loser': 15,
            'total_trades': 0
        }
    
    def calculate_position_size(self, confidence_score, direction='CALL'):
        """
        Calculate position size based on confidence and Kelly
        
        Args:
            confidence_score: 0-100 signal confidence
            direction: CALL/PUT
        
        Returns:
        {
            'risk_amount_usd': 12.50,
            'position_size_multiplier': 0.025,
            'kelly_fraction': 0.05,
            'confidence_adjusted': True,
            'recommendation': 'TAKE TRADE'
        }
        """
        # Minimum confidence threshold
        if confidence_score < 60:
            return {
                'risk_amount_usd': 0,
                'position_size_multiplier': 0,
                'kelly_fraction': 0,
                'confidence_adjusted': False,
                'recommendation': 'NO TRADE - LOW CONFIDENCE'
            }
        
        # Calculate Kelly fraction
        kelly_fraction = self._calculate_kelly()
        
        # Adjust for confidence (scale Kelly by confidence/100)
        confidence_multiplier = confidence_score / 100
        adjusted_kelly = kelly_fraction * confidence_multiplier
        
        # Half Kelly for safety
        safe_kelly = adjusted_kelly / 2
        
        # Cap at max risk
        max_position_fraction = self.max_risk_pct / 100
        final_fraction = min(safe_kelly, max_position_fraction)
        
        # Calculate USD risk
        risk_usd = self.account_size * final_fraction
        
        # Floor and ceiling
        if risk_usd < 10:
            risk_usd = 10  # Minimum viable trade
        
        if risk_usd > self.max_risk_usd:
            risk_usd = self.max_risk_usd
        
        # Recommendation
        if confidence_score >= 80:
            recommendation = 'STRONG TRADE - Full size'
        elif confidence_score >= 70:
            recommendation = 'GOOD TRADE - Normal size'
        else:
            recommendation = 'MARGINAL TRADE - Reduced size'
        
        return {
            'risk_amount_usd': round(risk_usd, 2),
            'position_size_multiplier': round(final_fraction, 4),
            'kelly_fraction': round(kelly_fraction, 4),
            'safe_kelly': round(safe_kelly, 4),
            'confidence_adjusted': True,
            'recommendation': recommendation,
            'max_allowed_risk': round(self.max_risk_usd, 2)
        }
    
    def _calculate_kelly(self):
        """Calculate Kelly criterion fraction"""
        stats = self.historical_stats
        
        # Need minimum trades for reliable Kelly
        if stats['total_trades'] < 10:
            # Conservative default until we have history
            return 0.02  # 2% per trade
        
        p = stats['win_rate']  # Probability of winning
        q = 1 - p              # Probability of losing
        
        # Win/loss ratio
        if stats['avg_loser'] > 0:
            b = stats['avg_winner'] / stats['avg_loser']
        else:
            b = 2.0  # Default 2:1
        
        # Kelly formula: f = (p*b - q) / b
        kelly = (p * b - q) / b
        
        # Never risk if Kelly is negative (no edge)
        if kelly <= 0:
            return 0
        
        # Cap Kelly at 10% (even if math says higher)
        return min(kelly, 0.10)
    
    def update_account_size(self, new_size):
        """Update account size (after wins/losses)"""
        self.account_size = new_size
        self.max_risk_usd = new_size * (self.max_risk_pct / 100)
        
        # Reload stats
        self.historical_stats = self._load_historical_stats()

if __name__ == "__main__":
    print("\n" + "="*100)
    print("KELLY POSITION SIZER TEST")
    print("="*100)
    
    sizer = KellyPositionSizer(account_size=500)
    
    print("\nAccount Size: $500")
    print(f"Max Risk: ${sizer.max_risk_usd:.2f} ({sizer.max_risk_pct}%)")
    
    print("\nPosition Sizing by Confidence:")
    
    for confidence in [85, 75, 65, 55]:
        result = sizer.calculate_position_size(confidence)
        print(f"\n  Confidence: {confidence}/100")
        print(f"    Risk: ${result['risk_amount_usd']:.2f}")
        print(f"    Kelly: {result['kelly_fraction']*100:.2f}%")
        print(f"    Recommendation: {result['recommendation']}")
    
    print("\n" + "="*100 + "\n")
