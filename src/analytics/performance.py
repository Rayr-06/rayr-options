"""
Performance Analytics
Calculate returns, win rate, Sharpe ratio, etc.
"""
import json
import os
from datetime import datetime
from pathlib import Path

class PerformanceAnalytics:
    def __init__(self):
        self.history_file = "data/results/history.json"
    
    def calculate(self):
        """Calculate all performance metrics"""
        if not os.path.exists(self.history_file):
            return self.default_metrics()
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            return self.default_metrics()
        
        # Get latest account value
        latest = history[-1]
        initial_capital = 100000  # Paper trading starts with $100k
        current_value = latest['account']['portfolio_value']
        
        total_return = ((current_value - initial_capital) / initial_capital) * 100
        
        # Count trades
        trades = [h for h in history if h.get('order')]
        
        return {
            'total_return_pct': total_return,
            'current_value': current_value,
            'initial_capital': initial_capital,
            'total_trades': len(trades),
            'days_running': self.days_running(history),
            'last_updated': datetime.now().isoformat()
        }
    
    def days_running(self, history):
        """Calculate days since first trade"""
        if not history:
            return 0
        
        first = datetime.fromisoformat(history[0]['timestamp'])
        return (datetime.now() - first).days
    
    def default_metrics(self):
        return {
            'total_return_pct': 0.0,
            'current_value': 100000.0,
            'initial_capital': 100000.0,
            'total_trades': 0,
            'days_running': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def save(self):
        """Save analytics to file"""
        metrics = self.calculate()
        
        Path("data").mkdir(exist_ok=True)
        
        with open("data/analytics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        return metrics

if __name__ == "__main__":
    analytics = PerformanceAnalytics()
    metrics = analytics.save()
    
    print("\n" + "="*80)
    print("PERFORMANCE METRICS")
    print("="*80)
    print(f"Total Return: {metrics['total_return_pct']:+.2f}%")
    print(f"Current Value: ${metrics['current_value']:,.2f}")
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Days Running: {metrics['days_running']}")
    print("="*80 + "\n")
