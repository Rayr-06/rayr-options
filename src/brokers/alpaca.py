"""
Alpaca Broker Integration
"""
import os
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

class AlpacaBroker:
    def __init__(self, paper=True):
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError("Missing Alpaca API keys")
        
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.paper = paper
        
        account = self.trading_client.get_account()
        print(f"\n{'PAPER' if paper else 'LIVE'} Trading Connected")
        print(f"Cash: ${float(account.cash):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}\n")
    
    def get_account(self):
        account = self.trading_client.get_account()
        return {
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'portfolio_value': float(account.portfolio_value),
            'equity': float(account.equity)
        }
    
    def get_quote(self, symbol):
        """Get latest quote for symbol"""
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = self.data_client.get_stock_latest_quote(request)
        
        if symbol not in quotes:
            return None
        
        quote = quotes[symbol]
        return {
            'symbol': symbol,
            'bid': float(quote.bid_price),
            'ask': float(quote.ask_price),
            'mid': (float(quote.bid_price) + float(quote.ask_price)) / 2,
            'timestamp': quote.timestamp
        }
    
    def buy_stock(self, symbol, qty):
        """Buy stock"""
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = self.trading_client.submit_order(order_data)
        
        return {
            'id': str(order.id),
            'symbol': order.symbol,
            'qty': str(order.qty),
            'side': str(order.side),
            'status': str(order.status),
            'submitted_at': str(order.submitted_at)
        }
    
    def get_positions(self):
        """Get all positions"""
        positions = self.trading_client.get_all_positions()
        
        return [{
            'symbol': pos.symbol,
            'qty': float(pos.qty),
            'avg_price': float(pos.avg_entry_price),
            'current_price': float(pos.current_price),
            'market_value': float(pos.market_value),
            'unrealized_pl': float(pos.unrealized_pl),
            'unrealized_plpc': float(pos.unrealized_plpc)
        } for pos in positions]
    
    def close_all_positions(self):
        """Close all positions"""
        return self.trading_client.close_all_positions(cancel_orders=True)
