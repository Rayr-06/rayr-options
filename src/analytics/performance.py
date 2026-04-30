"""
Advanced Analytics Engine - Hedge Fund Grade
Calculates all performance metrics, risk metrics, and health scores
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

class AdvancedAnalytics:
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
        
        # Get account data
        latest = history[-1]
        initial_capital = 100000
        current_value = latest['account']['portfolio_value']
        current_cash = latest['account']['cash']
        equity = current_value - current_cash
        
        # Get all trades
        trades = [h for h in history if h.get('order')]
        
        # Calculate returns
        total_return = ((current_value - initial_capital) / initial_capital) * 100
        total_profit = current_value - initial_capital
        
        # Time metrics
        if trades:
            first_trade = datetime.fromisoformat(trades[0]['timestamp'])
            days_running = max((datetime.now() - first_trade).days, 1)
        else:
            days_running = 1
        
        # Calculate daily/weekly/monthly returns
        daily_return = total_return / days_running if days_running > 0 else 0
        weekly_return = daily_return * 7
        monthly_return = daily_return * 30
        
        # Trade performance metrics
        trade_metrics = self.calculate_trade_metrics(trades, history)
        
        # Risk metrics
        risk_metrics = self.calculate_risk_metrics(history, current_value, initial_capital)
        
        # Ticker performance
        ticker_performance = self.calculate_ticker_performance(trades)
        
        # Time of day performance
        time_performance = self.calculate_time_performance(trades)
        
        # Market regime detection
        regime = self.detect_market_regime(history)
        
        # Health score (0-100)
        health_score = self.calculate_health_score(
            trade_metrics, 
            risk_metrics, 
            current_value, 
            initial_capital
        )
        
        # Kill switch status
        kill_switch = self.check_kill_switch(
            trade_metrics,
            risk_metrics,
            health_score
        )
        
        return {
            # Account
            'current_value': current_value,
            'current_cash': current_cash,
            'equity': equity,
            'initial_capital': initial_capital,
            
            # Returns
            'total_return_pct': total_return,
            'total_profit_usd': total_profit,
            'daily_return_pct': daily_return,
            'weekly_return_pct': weekly_return,
            'monthly_return_pct': monthly_return,
            
            # Time
            'days_running': days_running,
            'total_trades': len(trades),
            
            # Trade metrics
            'trade_metrics': trade_metrics,
            
            # Risk metrics
            'risk_metrics': risk_metrics,
            
            # Ticker performance
            'ticker_performance': ticker_performance,
            
            # Time performance
            'time_performance': time_performance,
            
            # Market regime
            'market_regime': regime,
            
            # Health & Safety
            'health_score': health_score,
            'kill_switch': kill_switch,
            
            # Recent trades
            'recent_trades': self.get_detailed_trades(trades[-20:]),
            
            'last_updated': datetime.now().isoformat()
        }
    
    def calculate_trade_metrics(self, trades, history):
        """Calculate trading performance metrics"""
        if not trades:
            return {
                'win_rate': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_winner': 0,
                'avg_loser': 0,
                'expectancy': 0,
                'profit_factor': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'avg_trade_duration_minutes': 0
            }
        
        winners = []
        losers = []
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for i, trade in enumerate(trades):
            if i > 0:
                prev_value = history[i-1]['account']['portfolio_value']
                curr_value = trade['account']['portfolio_value']
                profit = curr_value - prev_value
                
                if profit > 0:
                    winners.append(profit)
                    consecutive_wins += 1
                    consecutive_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                else:
                    losers.append(abs(profit))
                    consecutive_losses += 1
                    consecutive_wins = 0
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        win_rate = (len(winners) / len(trades) * 100) if trades else 0
        avg_winner = np.mean(winners) if winners else 0
        avg_loser = np.mean(losers) if losers else 0
        
        # Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        expectancy = (win_rate/100 * avg_winner) - ((100-win_rate)/100 * avg_loser)
        
        # Profit Factor = Gross Profit / Gross Loss
        gross_profit = sum(winners)
        gross_loss = sum(losers)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'win_rate': win_rate,
            'winning_trades': len(winners),
            'losing_trades': len(losers),
            'avg_winner': avg_winner,
            'avg_loser': avg_loser,
            'expectancy': expectancy,
            'profit_factor': profit_factor,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_trade_duration_minutes': 0  # TODO: calculate from timestamps
        }
    
    def calculate_risk_metrics(self, history, current_value, initial_capital):
        """Calculate risk and drawdown metrics"""
        if len(history) < 2:
            return {
                'max_drawdown_pct': 0,
                'max_drawdown_usd': 0,
                'current_drawdown_pct': 0,
                'current_drawdown_usd': 0,
                'daily_var_95': 0,
                'sharpe_ratio': 0,
                'volatility': 0
            }
        
        # Get equity curve
        equity_curve = [h['account']['portfolio_value'] for h in history]
        
        # Calculate drawdown
        peak = equity_curve[0]
        max_dd = 0
        current_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            max_dd = max(max_dd, dd)
            current_dd = dd
        
        max_dd_usd = peak - min(equity_curve)
        current_dd_usd = peak - current_value
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] * 100
            daily_returns.append(ret)
        
        # Volatility
        volatility = np.std(daily_returns) if daily_returns else 0
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(daily_returns, 5) if daily_returns else 0
        
        # Sharpe Ratio (simplified - assumes 0% risk-free rate)
        avg_return = np.mean(daily_returns) if daily_returns else 0
        sharpe = avg_return / volatility if volatility > 0 else 0
        
        return {
            'max_drawdown_pct': max_dd,
            'max_drawdown_usd': max_dd_usd,
            'current_drawdown_pct': current_dd,
            'current_drawdown_usd': current_dd_usd,
            'daily_var_95': var_95,
            'sharpe_ratio': sharpe,
            'volatility': volatility
        }
    
    def calculate_ticker_performance(self, trades):
        """Calculate performance by ticker"""
        tickers = {'SPY': [], 'QQQ': [], 'IWM': []}
        
        for i, trade in enumerate(trades):
            if i > 0:
                symbol = trade['opportunity']['symbol']
                # For now, we don't have individual trade P&L
                # We'll just count trades per ticker
                if symbol in tickers:
                    tickers[symbol].append(trade)
        
        result = {}
        for symbol in ['SPY', 'QQQ', 'IWM']:
            result[symbol] = {
                'trades': len(tickers[symbol]),
                'win_rate': 0,  # TODO: calculate actual win rate per ticker
                'total_pnl': 0,
                'avg_return': 0
            }
        
        return result
    
    def calculate_time_performance(self, trades):
        """Calculate performance by time of day"""
        time_buckets = {
            'morning': [],    # 9:30-11:00
            'midday': [],     # 11:00-14:00
            'afternoon': []   # 14:00-16:00
        }
        
        for trade in trades:
            hour = datetime.fromisoformat(trade['timestamp']).hour
            if 9 <= hour < 11:
                time_buckets['morning'].append(trade)
            elif 11 <= hour < 14:
                time_buckets['midday'].append(trade)
            else:
                time_buckets['afternoon'].append(trade)
        
        result = {}
        for period, trades_list in time_buckets.items():
            result[period] = {
                'trades': len(trades_list),
                'win_rate': 0,  # TODO: calculate actual win rate
                'avg_return': 0
            }
        
        return result
    
    def detect_market_regime(self, history):
        """Detect current market regime"""
        if len(history) < 5:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'description': 'Insufficient data'
            }
        
        # Simple regime detection based on recent price action
        recent = history[-5:]
        prices = [h['opportunity']['current_price'] for h in recent if h.get('opportunity')]
        
        if not prices:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'description': 'No price data'
            }
        
        # Calculate trend
        if len(prices) >= 3:
            if all(prices[i] < prices[i+1] for i in range(len(prices)-1)):
                return {
                    'regime': 'TRENDING_UP',
                    'confidence': 80,
                    'description': 'Strong uptrend - favor calls on pullbacks'
                }
            elif all(prices[i] > prices[i+1] for i in range(len(prices)-1)):
                return {
                    'regime': 'TRENDING_DOWN',
                    'confidence': 80,
                    'description': 'Strong downtrend - favor puts on bounces'
                }
        
        return {
            'regime': 'RANGING',
            'confidence': 60,
            'description': 'Choppy market - trade less, be selective'
        }
    
    def calculate_health_score(self, trade_metrics, risk_metrics, current_value, initial_capital):
        """Calculate system health score 0-100"""
        score = 100
        
        # Deduct for poor win rate
        if trade_metrics['win_rate'] < 40:
            score -= 20
        elif trade_metrics['win_rate'] < 50:
            score -= 10
        
        # Deduct for negative expectancy
        if trade_metrics['expectancy'] < 0:
            score -= 30
        
        # Deduct for low profit factor
        if trade_metrics['profit_factor'] < 1.0:
            score -= 20
        elif trade_metrics['profit_factor'] < 1.2:
            score -= 10
        
        # Deduct for high drawdown
        if risk_metrics['current_drawdown_pct'] > 10:
            score -= 20
        elif risk_metrics['current_drawdown_pct'] > 5:
            score -= 10
        
        # Deduct for consecutive losses
        if trade_metrics['consecutive_losses'] >= 3:
            score -= 20
        elif trade_metrics['consecutive_losses'] >= 2:
            score -= 10
        
        # Deduct for being down overall
        total_return = (current_value - initial_capital) / initial_capital * 100
        if total_return < -5:
            score -= 20
        elif total_return < 0:
            score -= 10
        
        return max(0, score)
    
    def check_kill_switch(self, trade_metrics, risk_metrics, health_score):
        """Check if trading should be paused"""
        reasons = []
        
        # Check consecutive losses
        if trade_metrics['consecutive_losses'] >= 3:
            reasons.append('3+ consecutive losses')
        
        # Check drawdown
        if risk_metrics['current_drawdown_pct'] > 8:
            reasons.append('Drawdown exceeds 8%')
        
        # Check health score
        if health_score < 60:
            reasons.append('Health score below 60')
        
        # Check profit factor
        if trade_metrics['total_trades'] >= 10 and trade_metrics['profit_factor'] < 0.8:
            reasons.append('Profit factor too low')
        
        return {
            'active': len(reasons) > 0,
            'reasons': reasons,
            'recommendation': 'PAUSE TRADING' if reasons else 'CONTINUE TRADING'
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
                'annual_return': opp.get('annual_return', 0),
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
            'days_running': 0,
            'total_trades': 0,
            'trade_metrics': {
                'win_rate': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_winner': 0,
                'avg_loser': 0,
                'expectancy': 0,
                'profit_factor': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'avg_trade_duration_minutes': 0
            },
            'risk_metrics': {
                'max_drawdown_pct': 0,
                'max_drawdown_usd': 0,
                'current_drawdown_pct': 0,
                'current_drawdown_usd': 0,
                'daily_var_95': 0,
                'sharpe_ratio': 0,
                'volatility': 0
            },
            'ticker_performance': {
                'SPY': {'trades': 0, 'win_rate': 0, 'total_pnl': 0, 'avg_return': 0},
                'QQQ': {'trades': 0, 'win_rate': 0, 'total_pnl': 0, 'avg_return': 0},
                'IWM': {'trades': 0, 'win_rate': 0, 'total_pnl': 0, 'avg_return': 0}
            },
            'time_performance': {
                'morning': {'trades': 0, 'win_rate': 0, 'avg_return': 0},
                'midday': {'trades': 0, 'win_rate': 0, 'avg_return': 0},
                'afternoon': {'trades': 0, 'win_rate': 0, 'avg_return': 0}
            },
            'market_regime': {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'description': 'Insufficient data'
            },
            'health_score': 100,
            'kill_switch': {
                'active': False,
                'reasons': [],
                'recommendation': 'CONTINUE TRADING'
            },
            'recent_trades': [],
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
    analytics = AdvancedAnalytics()
    metrics = analytics.save()
    
    print("\n" + "="*100)
    print("PROFESSIONAL ANALYTICS")
    print("="*100)
    print(f"Portfolio: ${metrics['current_value']:,.2f} | Return: {metrics['total_return_pct']:+.2f}%")
    print(f"Win Rate: {metrics['trade_metrics']['win_rate']:.1f}% | Expectancy: ${metrics['trade_metrics']['expectancy']:.2f}")
    print(f"Health Score: {metrics['health_score']}/100")
    print(f"Status: {metrics['kill_switch']['recommendation']}")
    print("="*100 + "\n")
