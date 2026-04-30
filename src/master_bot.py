"""
MASTER BOT - Main Trading System
Runs all strategies and executes trades
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from brokers.alpaca import AlpacaBroker
from strategies.options_premium import OptionsPremiumStrategy

class MasterBot:
    def __init__(self, paper=True):
        print("\n" + "="*100)
        print("RAYR OPTIONS - MASTER BOT")
        print(f"Mode: {'PAPER TRADING' if paper else 'LIVE TRADING'}")
        print("="*100 + "\n")
        
        self.broker = AlpacaBroker(paper=paper)
        self.strategy = OptionsPremiumStrategy(self.broker)
    
    def run(self):
        """Execute trading strategy"""
        try:
            # Get account info
            account = self.broker.get_account()
            
            print(f"Account Value: ${account['portfolio_value']:,.2f}")
            print(f"Cash Available: ${account['cash']:,.2f}\n")
            
            # Scan opportunities
            print("="*100)
            print("SCANNING MARKETS")
            print("="*100 + "\n")
            
            opportunities = self.strategy.scan()
            
            if not opportunities:
                print("No opportunities found\n")
                self.save_results(None, None, account)
                return
            
            # Display all opportunities
            print(f"Found {len(opportunities)} opportunities:\n")
            for i, opp in enumerate(opportunities, 1):
                print(f"{i}. {opp['symbol']}:")
                print(f"   Strike: ${opp['strike']:.2f} PUT")
                print(f"   Premium: ${opp['premium']:.2f}")
                print(f"   Weekly: {opp['return_pct']:.2f}%")
                print(f"   Annual: {opp['annual_return']:.1f}%\n")
            
            # Select best
            best = opportunities[0]
            
            print("="*100)
            print(f"SELECTED: {best['symbol']}")
            print("="*100)
            print(f"Strike: ${best['strike']:.2f} PUT")
            print(f"Premium: ${best['premium']:.2f}")
            print(f"Expected Return: {best['return_pct']:.2f}% weekly ({best['annual_return']:.1f}% annual)")
            print("\n")
            
            # Calculate position size
            shares = min(int(account['cash'] / best['current_price']), 10)
            
            if shares < 1:
                print("Insufficient funds\n")
                self.save_results(best, None, account)
                return
            
            print(f"Executing: Buy {shares} shares of {best['symbol']}")
            print(f"Cost: ${shares * best['current_price']:,.2f}\n")
            
            # Execute trade
            order = self.broker.buy_stock(best['symbol'], shares)
            
            print(f"✅ ORDER EXECUTED")
            print(f"Order ID: {order['id']}")
            print(f"Status: {order['status']}\n")
            
            # Save results
            self.save_results(best, order, account)
            
            # Show positions
            positions = self.broker.get_positions()
            
            if positions:
                print("="*100)
                print("CURRENT POSITIONS")
                print("="*100 + "\n")
                
                for pos in positions:
                    print(f"{pos['symbol']}:")
                    print(f"  Qty: {pos['qty']}")
                    print(f"  Avg Price: ${pos['avg_price']:.2f}")
                    print(f"  Current: ${pos['current_price']:.2f}")
                    print(f"  P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_plpc']*100:+.2f}%)\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            import traceback
            traceback.print_exc()
    
    def save_results(self, opportunity, order, account):
        """Save execution results"""
        Path("data/results").mkdir(parents=True, exist_ok=True)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'account': account,
            'opportunity': opportunity,
            'order': order
        }
        
        # Save individual trade
        if order:
            filename = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(f"data/results/{filename}", "w") as f:
                json.dump(result, f, indent=2)
        
        # Append to history
        history_file = "data/results/history.json"
        
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        history.append(result)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

if __name__ == "__main__":
    bot = MasterBot(paper=True)
    bot.run()
