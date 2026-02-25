"""
SOC-Lite Dashboard - Flask Web Interface
"""

from flask import Flask, render_template, jsonify, request
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.apache_parser import ApacheLogParser
from detection.brute_force_detector import detect_brute_force, get_summary


app = Flask(__name__)
app.config['SECRET_KEY'] = 'soc-lite-dev-key'


@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def api_stats():
    """Get general statistics"""
    # TODO: Connect to real data
    stats = {
        'total_logs': 5160,
        'total_attacks': 2,
        'unique_ips': 120,
        'time_range': '24 hours'
    }
    return jsonify(stats)


@app.route('/api/attacks')
def api_attacks():
    """Get detected attacks"""
    # TODO: Connect to real detection
    attacks = []
    return jsonify({'attacks': attacks})


if __name__ == '__main__':
    print("🛡️  SOC-Lite Dashboard")
    print("=" * 40)
    print("Starting server...")
    print("Access: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
