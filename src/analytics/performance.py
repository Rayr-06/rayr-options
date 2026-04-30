"""
Professional Performance Analytics
Real metrics for serious traders
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class ProAnalytics:
    def __init__(self):
        self.history_file = "data/results/history.json"
        self.positions_file = "data/positions.json"
    
    def calculate(self):
        """Calculate comprehensive trading metrics"""
        if not os.path.exists(self.history_file):
            return self.default_metrics()
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            return self.default_metrics()
        
        # Latest account snapshot
        latest = history[-1]
        initial_capital = 100000
        current_value = latest['account']['portfolio_value']
        current_cash = latest['account']['cash']
        
        # Calculate returns
        total_return = ((current_value - initial_capital) / initial_capital) * 100
        
        # Get all trades
        trades = [h for h in history if h.get('order')]
        
        # Calculate win rate and average returns
        winning_trades = 0
        total_profit = 0
        
        for i, trade in enumerate(trades):
            if i > 0:
                prev_value = history[i-1]['account']['portfolio_value']
                curr_value = trade['account']['portfolio_value']
                profit = curr_value - prev_value
                
                if profit > 0:
                    winning_trades += 1
                total_profit += profit
        
        win_rate = (winning_trades / len(trades) * 100) if trades else 0
        avg_profit = total_profit / len(trades) if trades else 0
        
        # Time-based returns
        first_trade = datetime.fromisoformat(history[0]['timestamp'])
        days_running = (datetime.now() - first_trade).days
        
        daily_return = total_return / days_running if days_running > 0 else 0
        weekly_return = daily_return * 7
        monthly_return = daily_return * 30
        
        return {
            # Account
            'current_value': current_value,
            'current_cash': current_cash,
            'equity': current_value - current_cash,
            'initial_capital': initial_capital,
            
            # Returns
            'total_return_pct': total_return,
            'total_profit_usd': current_value - initial_capital,
            'daily_return_pct': daily_return,
            'weekly_return_pct': weekly_return,
            'monthly_return_pct': monthly_return,
            
            # Trading stats
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': len(trades) - winning_trades,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            
            # Recent trades (last 10)
            'recent_trades': self.get_detailed_trades(trades[-10:]),
            
            # Time
            'days_running': days_running,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_detailed_trades(self, trades):
        """Get detailed trade information"""
        detailed = []
        
        for trade in trades:
            opp = trade.get('opportunity', {})
            order = trade.get('order', {})
            
            detailed.append({
                'timestamp': trade['timestamp'],
                'symbol': opp.get('symbol', 'N/A'),
                'strike': opp.get('strike', 0),
                'premium': opp.get('premium', 0),
                'return_pct': opp.get('return_pct', 0),
                'order_id': order.get('id', 'N/A'),
                'status': order.get('status', 'N/A')
            })
        
        return detailed
    
    def default_metrics(self):
        return {
            'current_value': 100000,
            'current_cash': 100000,
            'equity': 0,
            'initial_capital': 100000,
            'total_return_pct': 0,
            'total_profit_usd': 0,
            'daily_return_pct': 0,
            'weekly_return_pct': 0,
            'monthly_return_pct': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_profit_per_trade': 0,
            'recent_trades': [],
            'days_running': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def save(self):
        """Save analytics"""
        metrics = self.calculate()
        
        Path("data").mkdir(exist_ok=True)
        
        with open("data/analytics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        return metrics

if __name__ == "__main__":
    analytics = ProAnalytics()
    metrics = analytics.save()
    
    print("\n" + "="*80)
    print("PROFESSIONAL ANALYTICS")
    print("="*80)
    print(f"Portfolio Value: ${metrics['current_value']:,.2f}")
    print(f"Total Return: {metrics['total_return_pct']:+.2f}%")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Total Trades: {metrics['total_trades']}")
    print("="*80 + "\n")
