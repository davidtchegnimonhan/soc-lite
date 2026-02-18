"""
Benchmark parser performance.
Target: 10,000 logs in <2 seconds
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from datetime import datetime, timedelta
from parser.apache_parser import ApacheLogParser


def generate_logs(num_lines: int, filepath: str):
    """Generate synthetic Apache logs"""
    ips = [f"192.168.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(100)]
    endpoints = ["/", "/admin", "/login", "/api/users", "/static/css/main.css"]
    statuses = [200, 301, 400, 401, 403, 404, 500]

    start_time = datetime.now() - timedelta(days=1)

    with open(filepath, 'w') as f:
        for i in range(num_lines):
            ip = random.choice(ips)
            ts = (start_time + timedelta(seconds=i)).strftime("%d/%b/%Y:%H:%M:%S +0000")
            method = random.choice(["GET", "POST"])
            endpoint = random.choice(endpoints)
            status = random.choice(statuses)
            size = random.randint(100, 5000)
            f.write(f'{ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "Mozilla/5.0"\n')

    print(f"✅ Generated {num_lines:,} logs → {filepath}")


def run_benchmark(filepath: str, label: str):
    """Benchmark parser on a file"""
    log_parser = ApacheLogParser()

    times = []
    for _ in range(3):
        start = time.time()
        df = log_parser.parse_file(filepath, verbose=False)
        times.append(time.time() - start)

    avg = sum(times) / len(times)
    speed = len(df) / avg

    status = "✅ FAST" if avg < 2 else "⚠️  TOO SLOW"
    print(f"\n📊 {label}")
    print(f"   Logs   : {len(df):,}")
    print(f"   Time   : {avg:.3f}s")
    print(f"   Speed  : {speed:,.0f} logs/sec")
    print(f"   Status : {status}")
    return avg, speed


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    print("🔬 SOC-Lite Parser Benchmark")
    print("=" * 40)

    generate_logs(1_000,  'data/bench_1k.log')
    generate_logs(10_000, 'data/bench_10k.log')

    t1, s1 = run_benchmark('data/bench_1k.log',  '1,000 logs')
    t2, s2 = run_benchmark('data/bench_10k.log', '10,000 logs')

    print(f"\n🎯 Target: 10k logs in <2 sec → {'✅ PASSED' if t2 < 2 else '❌ FAILED'}")
