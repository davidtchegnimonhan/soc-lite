"""
Apache Log Parser - SOC-Lite
Parses Apache access logs into structured data.
"""

import re
import pandas as pd
from datetime import datetime
from typing import Optional, Dict


class ApacheLogParser:
    """Parser for Apache HTTP Server access logs."""
    
    # Apache Combined Log Format regex
    COMBINED_PATTERN = re.compile(
        r'^(\S+) '  # IP address
        r'\S+ \S+ '  # identd and user
        r'\[([^\]]+)\] '  # timestamp
        r'"(\S+) '  # method
        r'(\S+) '  # path/endpoint
        r'([^"]+)" '  # protocol
        r'(\d{3}) '  # status code
        r'(\d+|-) '  # size
        r'"([^"]*)" '  # referer
        r'"([^"]*)"'  # user-agent
    )
    
    def __init__(self, log_format: str = 'combined'):
        """Initialize parser."""
        self.log_format = log_format
        self.pattern = self.COMBINED_PATTERN
        
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse Apache timestamp to datetime object."""
        try:
            dt_str = timestamp_str.split()[0]
            return datetime.strptime(dt_str, '%d/%b/%Y:%H:%M:%S')
        except Exception:
            return None
    
    def parse_line(self, log_line: str) -> Optional[Dict]:
        """Parse a single Apache log line."""
        log_line = log_line.strip()
        
        if not log_line:
            return None
            
        match = self.pattern.match(log_line)
        
        if not match:
            return None
        
        ip, timestamp, method, path, protocol, status, size, referer, user_agent = match.groups()
        
        return {
            'ip': ip,
            'timestamp': self.parse_timestamp(timestamp),
            'method': method,
            'endpoint': path,
            'protocol': protocol,
            'status': int(status),
            'size': int(size) if size != '-' else 0,
            'referer': referer if referer != '-' else None,
            'user_agent': user_agent if user_agent != '-' else None
        }
    
    def parse_file(self, filepath: str, verbose: bool = True) -> pd.DataFrame:
        """Parse an entire log file."""
        parsed_logs = []
        invalid_count = 0
        total_lines = 0
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                
                parsed = self.parse_line(line)
                
                if parsed:
                    parsed_logs.append(parsed)
                else:
                    invalid_count += 1
                
                if verbose and line_num % 10000 == 0:
                    print(f"Processed {line_num} lines...")
        
        if verbose:
            print(f"\nParsing complete!")
            print(f"Total lines: {total_lines}")
            print(f"Successfully parsed: {len(parsed_logs)}")
            print(f"Invalid/skipped: {invalid_count}")
        
        return pd.DataFrame(parsed_logs)


def main():
    """Example usage."""
    parser = ApacheLogParser(log_format='combined')
    
    sample_log = '192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "http://example.com" "Mozilla/5.0"'
    
    parsed = parser.parse_line(sample_log)
    print("Parsed log entry:")
    print(parsed)


if __name__ == '__main__':
    main()
