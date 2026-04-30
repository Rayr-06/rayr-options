"""
Live API Server - Real-time bot control and monitoring
Runs on localhost:5000
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.signals.composite_score import CompositeScoreCalculator
from src.regime.market_regime import MarketRegimeDetector
from src.data.vix_data import VIXEngine
from src.data.market_data import MarketDataEngine

app = Flask(__name__)
CORS(app)

# Bot state
bot_state = {
    'running': False,
    'last_scan': None,
    'current_signals': None,
    'trade_log': [],
    'status': 'STOPPED'
}

# Initialize components
scorer = CompositeScoreCalculator()
regime_detector = MarketRegimeDetector()
vix_engine = VIXEngine()
market_data = MarketDataEngine()

def scan_markets():
    """Scan markets and return live signals"""
    try:
        # Get VIX state
        vix_state = vix_engine.get_vix_state()
        
        # Get market regime
        regime = regime_detector.detect_regime()
        
        # Scan opportunities
        scan = scorer.scan_all_symbols()
        
        # Get live market data
        spy_data = market_data.get_market_snapshot('SPY')
        qqq_data = market_data.get_market_snapshot('QQQ')
        iwm_data = market_data.get_market_snapshot('IWM')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'vix': vix_state,
            'regime': regime,
            'opportunities': scan['all_results'] if scan else [],
            'best_opportunity': scan['best_opportunity'] if scan else None,
            'market_data': {
                'SPY': spy_data,
                'QQQ': qqq_data,
                'IWM': iwm_data
            }
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@app.route('/api/status')
def get_status():
    return jsonify(bot_state)

@app.route('/api/scan', methods=['GET'])
def scan_now():
    signals = scan_markets()
    bot_state['last_scan'] = signals
    bot_state['current_signals'] = signals
    return jsonify(signals)

@app.route('/api/start', methods=['POST'])
def start_bot():
    bot_state['running'] = True
    bot_state['status'] = 'RUNNING'
    bot_state['trade_log'].append({
        'timestamp': datetime.now().isoformat(),
        'action': 'BOT_STARTED',
        'message': 'Trading bot started'
    })
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot_state['running'] = False
    bot_state['status'] = 'STOPPED'
    bot_state['trade_log'].append({
        'timestamp': datetime.now().isoformat(),
        'action': 'BOT_STOPPED',
        'message': 'Trading bot stopped'
    })
    return jsonify({'status': 'stopped'})

@app.route('/api/logs')
def get_logs():
    return jsonify(bot_state['trade_log'][-50:])

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("LIVE CONTROL DASHBOARD API")
    print("="*60)
    print(f"\nRunning on: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /api/status  - Bot status")
    print("  GET  /api/scan    - Scan markets now")
    print("  POST /api/start   - Start bot")
    print("  POST /api/stop    - Stop bot")
    print("  GET  /api/logs    - Trade logs")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

