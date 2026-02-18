"""
SOC-Lite - Main Entry Point

Usage:
    python main.py --log <logfile>
    python main.py --log logs/sample.log --threshold 5
"""

import argparse
from parser.apache_parser import ApacheLogParser
from detection.brute_force_detector import detect_brute_force, get_summary


def main():
    parser_args = argparse.ArgumentParser(
        description='SOC-Lite: Lightweight SIEM for Apache logs'
    )
    parser_args.add_argument('--log', required=True, help='Path to Apache log file')
    parser_args.add_argument('--threshold', type=int, default=10, help='Brute force threshold')
    parser_args.add_argument('--window', type=int, default=5, help='Time window in minutes')
    args = parser_args.parse_args()

    print("=" * 50)
    print("🛡️  SOC-Lite - Security Log Analyzer")
    print("=" * 50)

    # Parse logs
    print(f"\n[1/2] Parsing logs: {args.log}")
    log_parser = ApacheLogParser()
    df = log_parser.parse_file(args.log)

    # Detect attacks
    print(f"\n[2/2] Detecting brute force attacks...")
    print(f"      Threshold: {args.threshold} attempts in {args.window} min")
    attacks = detect_brute_force(df, window_minutes=args.window, threshold=args.threshold)

    # Results
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    summary = get_summary(attacks)
    print(f"Total logs analyzed : {len(df):,}")
    print(f"Attacks detected    : {summary['total_attacks']}")

    if summary['total_attacks'] > 0:
        print(f"Top attacker        : {summary['top_attacker']}")
        print(f"Max attempts        : {summary['max_attempts']}")
        print(f"\nDetailed attacks:")
        print(attacks.to_string(index=False))


if __name__ == '__main__':
    main()
