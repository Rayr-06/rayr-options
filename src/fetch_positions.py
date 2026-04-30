"""
Live Position Tracker
Fetches current positions from Alpaca
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from brokers.alpaca import AlpacaBroker

def fetch_live_positions():
    """Get current positions from Alpaca"""
    try:
        broker = AlpacaBroker(paper=True)
        account = broker.get_account()
        positions = broker.get_positions()
        
        data = {
            'account': account,
            'positions': positions,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        Path("data").mkdir(exist_ok=True)
        
        with open("data/positions.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Fetched {len(positions)} positions")
        print(f"  Portfolio: ${account['portfolio_value']:,.2f}")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    fetch_live_positions()
