"""
Master Bot Orchestrator - Professional Trading System
Brings everything together
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from signals.composite_score import CompositeScoreCalculator
from regime.market_regime import MarketRegimeDetector
from risk.position_sizer import KellyPositionSizer
from data.vix_data import VIXEngine
from brokers.alpaca import AlpacaBroker
import json
from datetime import datetime

class MasterBot:
    """
    Professional Trading System Orchestrator
    
    Workflow:
    1. Check market regime
    2. Check VIX state
    3. Scan for opportunities (SPY/QQQ/IWM)
    4. Calculate composite scores
    5. Select best opportunity
    6. Size position with Kelly
    7. Execute trade
    8. Log everything
    
    Safety:
    - Regime-aware trading
    - VIX-based position sizing
    - Confidence thresholds
    - Kelly position sizing
    - Max daily loss limits
    """
    
    def __init__(self, paper_trading=True):
        self.paper_trading = paper_trading
        
        # Initialize components
        self.scorer = CompositeScoreCalculator()
        self.regime_detector = MarketRegimeDetector()
        self.position_sizer = KellyPositionSizer(account_size=100000)  # Paper account
        self.vix = VIXEngine()
        self.broker = AlpacaBroker(paper=paper_trading)
        
        # Safety limits
        self.max_daily_loss = 250  # $250 max loss per day
        self.min_confidence = 60   # Minimum 60/100 confidence
        
        # State
        self.daily_pnl = 0
    
    def run(self):
        """Main trading loop"""
        print("\n" + "="*100)
        print("MASTER BOT - PROFESSIONAL TRADING SYSTEM")
        print("="*100)
        
        # Step 1: Check if we should trade today
        if not self._should_trade_today():
            print("\n❌ NOT TRADING TODAY - Conditions not met")
            return None
        
        # Step 2: Detect market regime
        regime = self.regime_detector.detect_regime()
        print(f"\n📊 Market Regime: {regime['primary_regime']} (Confidence: {regime['confidence']}%)")
        print(f"   VIX: {regime['vix_level']:.2f} ({regime['vix_regime']})")
        
        # Step 3: Scan for opportunities
        print("\n🔍 Scanning opportunities...")
        scan = self.scorer.scan_all_symbols()
        
        if not scan:
            print("   No opportunities found")
            return None
        
        # Step 4: Get best opportunity
        best = scan['best_opportunity']
        
        print(f"\n✨ Best Opportunity: {best['symbol']}")
        print(f"   Confidence: {best['confidence']}/100")
        print(f"   Direction: {best['direction']}")
        print(f"   Trade Type: {best['trade_type']}")
        print(f"   Recommendation: {best['recommendation']}")
        
        # Step 5: Check if confidence meets threshold
        if best['confidence'] < self.min_confidence:
            print(f"\n❌ Confidence too low ({best['confidence']}/100 < {self.min_confidence}/100)")
            return None
        
        # Step 6: Check VIX restrictions
        if not best['vix_state']['allow_premium_selling'] and best['trade_type'] == 'PREMIUM_SELLING':
            print(f"\n❌ VIX too high for premium selling ({best['vix_state']['vix_level']:.2f})")
            return None
        
        # Step 7: Calculate position size
        position = self.position_sizer.calculate_position_size(best['confidence'], best['direction'])
        
        print(f"\n💰 Position Sizing:")
        print(f"   Risk Amount: ${position['risk_amount_usd']:.2f}")
        print(f"   Kelly Fraction: {position['kelly_fraction']*100:.2f}%")
        print(f"   Recommendation: {position['recommendation']}")
        
        if position['risk_amount_usd'] == 0:
            print("\n❌ Position size = 0, skipping trade")
            return None
        
        # Step 8: Execute trade (placeholder)
        print(f"\n🚀 EXECUTING TRADE:")
        print(f"   Symbol: {best['symbol']}")
        print(f"   Direction: {best['direction']}")
        print(f"   Risk: ${position['risk_amount_usd']:.2f}")
        print(f"   Strategy: {best['trade_type']}")
        
        # TODO: Replace with real options execution
        trade_result = self._execute_placeholder_trade(best, position, regime)
        
        # Step 9: Log trade
        self._log_trade(trade_result)
        
        print("\n" + "="*100 + "\n")
        
        return trade_result
    
    def _should_trade_today(self):
        """Check if we should trade today"""
        
        # Check daily loss limit
        if self.daily_pnl < -self.max_daily_loss:
            print(f"   Daily loss limit hit (${self.daily_pnl:.2f})")
            return False
        
        # Check market hours (9:30 AM - 4:00 PM ET)
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        # For testing, allow anytime
        # In production, check: 9 <= hour < 16 and not (hour == 9 and minute < 30)
        
        return True
    
    def _execute_placeholder_trade(self, opportunity, position, regime):
        """
        Placeholder trade execution
        
        TODO: Replace with real options execution using:
        - opportunity['symbol']
        - opportunity['direction'] (CALL/PUT)
        - position['risk_amount_usd']
        - regime['strategy_guidance']
        """
        return {
            'symbol': opportunity['symbol'],
            'direction': opportunity['direction'],
            'strategy': opportunity['trade_type'],
            'confidence': opportunity['confidence'],
            'risk_usd': position['risk_amount_usd'],
            'regime': regime['primary_regime'],
            'timestamp': datetime.now().isoformat(),
            'status': 'SIMULATED'
        }
    
    def _log_trade(self, trade):
        """Log trade to file"""
        os.makedirs('data/results', exist_ok=True)
        
        log_file = f"data/results/master_bot_trades.json"
        
        # Load existing logs
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Append new trade
        logs.append(trade)
        
        # Save
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"\n✓ Trade logged to {log_file}")

if __name__ == "__main__":
    bot = MasterBot(paper_trading=True)
    bot.run()
