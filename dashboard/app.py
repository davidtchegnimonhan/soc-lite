"""
SOC-Lite Dashboard - Flask Web Interface (Secured)
"""

from flask import Flask, render_template, jsonify, request, send_file
import sys
import os
import io
import csv
import json as json_module
import secrets
import re
from functools import wraps

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.apache_parser import ApacheLogParser
from detection.brute_force_detector import detect_brute_force, get_summary


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Simple rate limiting (in-memory)
from collections import defaultdict
from time import time

rate_limit_store = defaultdict(list)

def rate_limit(max_calls, period):
    """Simple rate limiter decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time()
            key = request.remote_addr
            
            # Clean old entries
            rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < period]
            
            # Check limit
            if len(rate_limit_store[key]) >= max_calls:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            rate_limit_store[key].append(now)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # XSS Protection
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # CSP
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self';"
    )
    
    # HSTS (if using HTTPS)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


# Input validation
def validate_ip_filter(ip_string):
    """Validate IP filter input (partial IP allowed)"""
    if not ip_string:
        return True
    # Allow partial IPs like "203.0.113" or full IPs
    pattern = r'^[\d.]+$'
    return bool(re.match(pattern, ip_string)) and len(ip_string) <= 15


def validate_severity(severity):
    """Validate severity input"""
    valid_severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    return severity in valid_severities


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
@rate_limit(max_calls=30, period=60)  # 30 calls per minute
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
@rate_limit(max_calls=30, period=60)
def api_attacks():
    """Get detected attacks with optional filters"""
    # Get and validate filter parameters
    severity_filter = request.args.get('severity', 'ALL')
    ip_filter = request.args.get('ip', '')
    
    # Input validation
    if not validate_severity(severity_filter):
        return jsonify({'error': 'Invalid severity filter'}), 400
    
    if not validate_ip_filter(ip_filter):
        return jsonify({'error': 'Invalid IP filter'}), 400
    
    if attacks_df.empty:
        return jsonify({'attacks': []})
    
    # Apply filters (server-side, safe)
    filtered_df = attacks_df.copy()
    
    if severity_filter != 'ALL':
        filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
    
    if ip_filter:
        # Safe filter: exact string matching, no regex
        filtered_df = filtered_df[filtered_df['ip'].str.contains(ip_filter, case=False, regex=False)]
    
    # Convert to list (data already sanitized from detection)
    attacks = []
    for _, row in filtered_df.iterrows():
        attacks.append({
            'ip': str(row['ip']),  # Ensure string
            'attempts': int(row['attempts']),
            'severity': str(row['severity']),
            'endpoints': str(row['endpoints']),
            'first_seen': str(row['first_seen']),
            'last_seen': str(row['last_seen'])
        })
    
    return jsonify({'attacks': attacks})


@app.route('/api/timeline')
@rate_limit(max_calls=30, period=60)
def api_timeline():
    """Get attack timeline data for charts"""
    if attacks_df.empty:
        return jsonify({'labels': [], 'data': []})
    
    # Simple timeline: attacks by IP
    timeline = {
        'labels': [str(ip) for ip in attacks_df['ip'].tolist()],
        'data': [int(attempts) for attempts in attacks_df['attempts'].tolist()]
    }
    return jsonify(timeline)


@app.route('/api/export/<format>')
@rate_limit(max_calls=5, period=60)  # Stricter limit for exports
def export_attacks(format):
    """Export attacks to CSV or JSON"""
    # Validate format
    if format not in ['csv', 'json']:
        return jsonify({'error': 'Invalid format. Use csv or json'}), 400
    
    if attacks_df.empty:
        return jsonify({'error': 'No attacks to export'}), 404
    
    if format == 'csv':
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['IP', 'Attempts', 'Severity', 'Endpoints', 'First Seen', 'Last Seen'])
        
        # Write data (already sanitized)
        for _, row in attacks_df.iterrows():
            writer.writerow([
                str(row['ip']),
                int(row['attempts']),
                str(row['severity']),
                str(row['endpoints']),
                str(row['first_seen']),
                str(row['last_seen'])
            ])
        
        # Prepare file for download
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='soc_lite_attacks.csv'
        )
    
    elif format == 'json':
        # Convert to JSON (data already sanitized)
        attacks = []
        for _, row in attacks_df.iterrows():
            attacks.append({
                'ip': str(row['ip']),
                'attempts': int(row['attempts']),
                'severity': str(row['severity']),
                'endpoints': str(row['endpoints']),
                'first_seen': str(row['first_seen']),
                'last_seen': str(row['last_seen'])
            })
        
        # Prepare JSON for download
        json_str = json_module.dumps({'attacks': attacks}, indent=2)
        return send_file(
            io.BytesIO(json_str.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name='soc_lite_attacks.json'
        )


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n🛡️  SOC-Lite Dashboard (Secured)")
    print("=" * 40)
    print("Starting server...")
    print("Access: http://localhost:5000")
    print("=" * 40)
    print("\n⚠️  Security Notes:")
    print("- Rate limiting enabled")
    print("- Input validation active")
    print("- XSS protection enabled")
    print("- CSP headers set")
    print("\n⚠️  For production:")
    print("- Use HTTPS")
    print("- Add authentication")
    print("- Use production WSGI server (gunicorn)")
    print("=" * 40)
    app.run(debug=True, host='0.0.0.0', port=5000)
