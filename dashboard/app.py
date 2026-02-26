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

# Load data at startup
print("📊 Loading log data...")
parser = ApacheLogParser()
df = parser.parse_file('data/attack_dataset.log', verbose=False)
attacks_df = detect_brute_force(df, threshold=10, window_minutes=5)
summary = get_summary(attacks_df)

print(f"✅ Loaded {len(df)} logs, detected {summary['total_attacks']} attacks")


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
    stats = {
        'total_logs': len(df),
        'total_attacks': summary['total_attacks'],
        'unique_ips': int(df['ip'].nunique()),
        'time_range': '6 hours'
    }
    return jsonify(stats)


@app.route('/api/attacks')
def api_attacks():
    """Get detected attacks"""
    if attacks_df.empty:
        return jsonify({'attacks': []})
    
    attacks = []
    for _, row in attacks_df.iterrows():
        attacks.append({
            'ip': row['ip'],
            'attempts': int(row['attempts']),
            'severity': row['severity'],
            'endpoints': row['endpoints'],
            'first_seen': str(row['first_seen']),
            'last_seen': str(row['last_seen'])
        })
    
    return jsonify({'attacks': attacks})


@app.route('/api/timeline')
def api_timeline():
    """Get attack timeline data for charts"""
    if attacks_df.empty:
        return jsonify({'labels': [], 'data': []})
    
    # Simple timeline: attacks by IP
    timeline = {
        'labels': attacks_df['ip'].tolist(),
        'data': attacks_df['attempts'].tolist()
    }
    return jsonify(timeline)


if __name__ == '__main__':
    print("\n🛡️  SOC-Lite Dashboard")
    print("=" * 40)
    print("Starting server...")
    print("Access: http://localhost:5000")
    print("=" * 40)
    app.run(debug=True, host='0.0.0.0', port=5000)
