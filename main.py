"""
SOC-Lite - Main Entry Point
Usage:
    python main.py --log <logfile>
    python main.py --log logs/sample.log --threshold 5
"""

import argparse
from parser.format_detector import FormatDetector
from detection.brute_force_detector import detect_brute_force, get_summary


def main():
    parser_args = argparse.ArgumentParser(
        description='SOC-Lite: Lightweight SIEM for Apache/Nginx logs'
    )
    parser_args.add_argument('--log', required=True, help='Path to log file')
    parser_args.add_argument('--threshold', type=int, default=10, help='Brute force threshold')
    parser_args.add_argument('--window', type=int, default=5, help='Time window in minutes')
    parser_args.add_argument('--format', choices=['apache', 'nginx', 'auto'], default='auto',
                           help='Log format (auto-detected by default)')
    
    args = parser_args.parse_args()
    
    print("=" * 50)
    print("🛡️  SOC-Lite - Security Log Analyzer")
    print("=" * 50)
    
    # Get appropriate parser
    print(f"\n[1/3] Detecting log format...")
    if args.format == 'auto':
        log_parser = FormatDetector.get_parser(args.log)
    elif args.format == 'apache':
        from parser.apache_parser import ApacheLogParser
        log_parser = ApacheLogParser()
        print("✅ Using Apache parser")
    else:
        from parser.nginx_parser import NginxLogParser
        log_parser = NginxLogParser()
        print("✅ Using Nginx parser")
    
    # Parse logs
    print(f"\n[2/3] Parsing logs: {args.log}")
    df = log_parser.parse_file(args.log)
    
    if df.empty:
        print("❌ No logs parsed. Check file format.")
        return
    
    # Detect attacks
    print(f"\n[3/3] Detecting brute force attacks...")
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
        print(attacks[['ip', 'attempts', 'severity', 'endpoints']].to_string(index=False))
    else:
        print("✅ No attacks detected!")


if __name__ == '__main__':
    main()
