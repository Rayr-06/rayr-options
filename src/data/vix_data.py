"""
VIX Data Engine - Market Fear Gauge
Professional volatility state machine
"""
import os
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

class VIXEngine:
    """
    VIX State Machine
    
    States:
    - COMPLACENT: VIX < 15 (sell premium)
    - NORMAL: VIX 15-20 (selective trades)
    - ELEVATED: VIX 20-30 (reduce size)
    - FEAR: VIX > 30 (pause or buy protection)
    
    CRITICAL RULE: Never sell premium when VIX > 30
    """
    
    def __init__(self):
        self.client = StockHistoricalDataClient(
            api_key=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_SECRET_KEY')
        )
    
    def get_vix_level(self):
        """Get current VIX level"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=['VIX'])
            quotes = self.client.get_stock_latest_quote(request)
            
            if 'VIX' in quotes:
                vix_value = (quotes['VIX'].bid_price + quotes['VIX'].ask_price) / 2
                return float(vix_value)
            
            # Fallback: Estimate from SPY movement
            return self._estimate_vix_from_spy()
        
        except Exception as e:
            print(f"VIX fetch error: {e}")
            return self._estimate_vix_from_spy()
    
    def _estimate_vix_from_spy(self):
        """Estimate VIX from SPY volatility (fallback)"""
        try:
            request = StockBarsRequest(
                symbol_or_symbols='SPY',
                timeframe=TimeFrame(5, TimeFrame.Minute),
                start=datetime.now() - timedelta(days=1),
                limit=50
            )
            
            bars = self.client.get_stock_bars(request)
            
            if 'SPY' not in bars:
                return 15.0  # Conservative default
            
            # Calculate realized volatility
            closes = [float(bar.close) for bar in bars['SPY']]
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            
            # Annualized volatility
            std_dev = sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)
            volatility = (std_dev ** 0.5) * (252 ** 0.5) * 100
            
            return volatility
        
        except:
            return 15.0
    
    def get_vix_state(self):
        """
        Get VIX state and trading recommendations
        
        Returns:
        - state: COMPLACENT/NORMAL/ELEVATED/FEAR
        - vix_level: Current VIX
        - recommendation: Trading guidance
        - position_size_multiplier: 1.0 = normal, 0.5 = half size, 0 = no trading
        """
        vix = self.get_vix_level()
        
        if vix < 15:
            return {
                'state': 'COMPLACENT',
                'vix_level': vix,
                'recommendation': 'SELL PREMIUM - Low volatility environment',
                'position_size_multiplier': 1.0,
                'allow_premium_selling': True
            }
        elif vix < 20:
            return {
                'state': 'NORMAL',
                'vix_level': vix,
                'recommendation': 'SELECTIVE TRADES - Normal volatility',
                'position_size_multiplier': 1.0,
                'allow_premium_selling': True
            }
        elif vix < 30:
            return {
                'state': 'ELEVATED',
                'vix_level': vix,
                'recommendation': 'REDUCE SIZE - Elevated volatility',
                'position_size_multiplier': 0.5,
                'allow_premium_selling': True
            }
        else:
            return {
                'state': 'FEAR',
                'vix_level': vix,
                'recommendation': 'PAUSE PREMIUM SELLING - High fear',
                'position_size_multiplier': 0.0,
                'allow_premium_selling': False
            }

if __name__ == "__main__":
    engine = VIXEngine()
    state = engine.get_vix_state()
    
    print("\n" + "="*100)
    print("VIX STATE MACHINE")
    print("="*100)
    print(f"\nVIX Level: {state['vix_level']:.2f}")
    print(f"State: {state['state']}")
    print(f"Recommendation: {state['recommendation']}")
    print(f"Position Size: {state['position_size_multiplier']*100:.0f}%")
    print("\n" + "="*100 + "\n")
