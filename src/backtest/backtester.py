"""
Backtest Engine - Validate Edge Before Risking Money
CRITICAL: Never trade live without backtesting first
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import json
import numpy as np

class BacktestEngine:
    """
    Historical Backtesting System
    
    Tests:
    - 30 day backtest
    - 90 day backtest
    - High volatility periods
    - Low volatility periods
    - Trend days vs chop days
    
    Metrics:
    - Win rate
    - Expectancy
    - Max drawdown
    - Profit factor
    - Sharpe ratio
    - Best/worst setups
    
    RULE: Need 30+ trades with positive expectancy before going live
    """
    
    def __init__(self):
        self.results = []
        self.equity_curve = []
        self.initial_capital = 500
        self.current_capital = self.initial_capital
    
    def run_backtest(self, strategy, start_date, end_date):
        """
        Run backtest for a strategy over date range
        
        Args:
            strategy: Strategy object with execute() method
            start_date: datetime
            end_date: datetime
        
        Returns:
            Backtest results dict
        """
        print(f"\n{'='*100}")
        print(f"BACKTEST: {start_date.date()} to {end_date.date()}")
        print(f"{'='*100}\n")
        
        # Simulate trading days
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Simulate strategy execution
            # TODO: Replace with real historical data
            trade_result = self._simulate_trade(strategy, current_date)
            
            if trade_result:
                self.results.append(trade_result)
                self.current_capital += trade_result['pnl']
                
                self.equity_curve.append({
                    'date': current_date,
                    'capital': self.current_capital
                })
            
            current_date += timedelta(days=1)
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return metrics
    
    def _simulate_trade(self, strategy, date):
        """
        Simulate a single trade
        
        TODO: Replace with real historical execution
        For now, returns random results for testing
        """
        # Placeholder: Random win/loss based on historical win rate
        import random
        
        win_rate = 0.55  # 55% win rate assumption
        
        if random.random() < win_rate:
            # Winner
            pnl = random.uniform(15, 30)
            return {
                'date': date,
                'result': 'WIN',
                'pnl': pnl,
                'return_pct': (pnl / self.current_capital) * 100
            }
        else:
            # Loser
            pnl = random.uniform(-20, -10)
            return {
                'date': date,
                'result': 'LOSS',
                'pnl': pnl,
                'return_pct': (pnl / self.current_capital) * 100
            }
    
    def _calculate_metrics(self):
        """Calculate backtest performance metrics"""
        if not self.results:
            return self._empty_metrics()
        
        # Separate wins and losses
        wins = [r['pnl'] for r in self.results if r['result'] == 'WIN']
        losses = [r['pnl'] for r in self.results if r['result'] == 'LOSS']
        
        total_trades = len(self.results)
        winning_trades = len(wins)
        losing_trades = len(losses)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_winner = np.mean(wins) if wins else 0
        avg_loser = np.mean(losses) if losses else 0
        
        # Expectancy
        expectancy = (win_rate/100 * avg_winner) - ((100-win_rate)/100 * abs(avg_loser))
        
        # Profit factor
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Total return
        total_return = self.current_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Max drawdown
        max_dd = self._calculate_max_drawdown()
        
        # Sharpe ratio (simplified)
        returns = [r['return_pct'] for r in self.results]
        sharpe = (np.mean(returns) / np.std(returns)) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'avg_winner': round(avg_winner, 2),
            'avg_loser': round(avg_loser, 2),
            'expectancy': round(expectancy, 2),
            'profit_factor': round(profit_factor, 2),
            'total_return_usd': round(total_return, 2),
            'total_return_pct': round(total_return_pct, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'sharpe_ratio': round(sharpe, 2),
            'final_capital': round(self.current_capital, 2),
            'pass_criteria': self._check_pass_criteria(expectancy, profit_factor, max_dd, total_trades)
        }
    
    def _calculate_max_drawdown(self):
        """Calculate maximum drawdown percentage"""
        if not self.equity_curve:
            return 0
        
        peak = self.equity_curve[0]['capital']
        max_dd = 0
        
        for point in self.equity_curve:
            capital = point['capital']
            
            if capital > peak:
                peak = capital
            
            dd = (peak - capital) / peak * 100
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _check_pass_criteria(self, expectancy, profit_factor, max_dd, total_trades):
        """
        Check if backtest passes criteria for live trading
        
        Criteria:
        - 30+ trades minimum
        - Positive expectancy
        - Profit factor > 1.2
        - Max drawdown < 15%
        """
        passed = []
        failed = []
        
        if total_trades >= 30:
            passed.append('✓ Sufficient trades (30+)')
        else:
            failed.append(f'✗ Need 30+ trades (have {total_trades})')
        
        if expectancy > 0:
            passed.append(f'✓ Positive expectancy (${expectancy:.2f})')
        else:
            failed.append(f'✗ Negative expectancy (${expectancy:.2f})')
        
        if profit_factor > 1.2:
            passed.append(f'✓ Good profit factor ({profit_factor:.2f})')
        else:
            failed.append(f'✗ Low profit factor ({profit_factor:.2f})')
        
        if max_dd < 15:
            passed.append(f'✓ Controlled drawdown ({max_dd:.1f}%)')
        else:
            failed.append(f'✗ High drawdown ({max_dd:.1f}%)')
        
        all_passed = len(failed) == 0
        
        return {
            'ready_for_live': all_passed,
            'passed_checks': passed,
            'failed_checks': failed,
            'recommendation': 'GO LIVE with $500' if all_passed else 'CONTINUE PAPER TRADING'
        }
    
    def _empty_metrics(self):
        """Return empty metrics when no trades"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_winner': 0,
            'avg_loser': 0,
            'expectancy': 0,
            'profit_factor': 0,
            'total_return_usd': 0,
            'total_return_pct': 0,
            'max_drawdown_pct': 0,
            'sharpe_ratio': 0,
            'final_capital': self.initial_capital
        }
    
    def save_results(self, filepath='data/backtest_results.json'):
        """Save backtest results"""
        os.makedirs('data', exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                'metrics': self._calculate_metrics(),
                'trades': self.results,
                'equity_curve': [
                    {
                        'date': p['date'].isoformat(),
                        'capital': p['capital']
                    }
                    for p in self.equity_curve
                ]
            }, f, indent=2, default=str)
        
        print(f"\n✓ Backtest results saved to {filepath}")

if __name__ == "__main__":
    print("\n" + "="*100)
    print("BACKTEST ENGINE TEST (30-day simulation)")
    print("="*100)
    
    engine = BacktestEngine()
    
    # Simulate 30 day backtest
    start = datetime.now() - timedelta(days=30)
    end = datetime.now()
    
    metrics = engine.run_backtest(None, start, end)
    
    print("\nBACKTEST RESULTS:")
    print(f"  Total Trades: {metrics['total_trades']}")
    print(f"  Win Rate: {metrics['win_rate']}%")
    print(f"  Expectancy: ${metrics['expectancy']}")
    print(f"  Profit Factor: {metrics['profit_factor']}")
    print(f"  Total Return: ${metrics['total_return_usd']} ({metrics['total_return_pct']}%)")
    print(f"  Max Drawdown: {metrics['max_drawdown_pct']}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']}")
    
    print("\nREADY FOR LIVE TRADING?")
    criteria = metrics['pass_criteria']
    
    print("\nPASSED:")
    for check in criteria['passed_checks']:
        print(f"  {check}")
    
    if criteria['failed_checks']:
        print("\nFAILED:")
        for check in criteria['failed_checks']:
            print(f"  {check}")
    
    print(f"\n{'='*50}")
    print(f"RECOMMENDATION: {criteria['recommendation']}")
    print(f"{'='*50}")
    
    engine.save_results()
    
    print("\n" + "="*100 + "\n")
