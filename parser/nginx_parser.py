"""
Nginx Log Parser - SOC-Lite
Supports Nginx combined log format
"""

import re
import pandas as pd
from datetime import datetime
from typing import Optional, Dict


class NginxLogParser:
    """Parser for Nginx logs (combined format)"""
    
    def __init__(self, log_format: str = 'combined'):
        """
        Initialize Nginx parser
        
        Args:
            log_format: 'combined' or 'access'
        """
        self.log_format = log_format
        
        # Nginx combined format regex
        # Format: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
        self.pattern = re.compile(
            r'(?P<ip>[\d\.]+)\s+'                      # IP address
            r'-\s+'                                      # Separator
            r'(?P<user>\S+)\s+'                         # Remote user
            r'\[(?P<timestamp>[^\]]+)\]\s+'            # Timestamp
            r'"(?P<method>\S+)\s+'                      # HTTP method
            r'(?P<endpoint>\S+)\s+'                     # Endpoint/path
            r'(?P<protocol>[^"]+)"\s+'                  # HTTP protocol
            r'(?P<status>\d{3})\s+'                     # Status code
            r'(?P<size>\S+)\s+'                         # Body bytes sent
            r'"(?P<referrer>[^"]*)"\s+'                 # Referer
            r'"(?P<user_agent>[^"]*)"'                  # User agent
        )
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse Nginx timestamp format
        
        Args:
            timestamp_str: Timestamp string (e.g., "03/Mar/2026:10:30:45 +0000")
            
        Returns:
            datetime object
        """
        try:
            # Nginx format: "DD/Mon/YYYY:HH:MM:SS +ZZZZ"
            return datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            # Fallback without timezone
            try:
                return datetime.strptime(timestamp_str.split()[0], "%d/%b/%Y:%H:%M:%S")
            except:
                return datetime.now()
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single Nginx log line
        
        Args:
            line: Raw log line
            
        Returns:
            Dictionary with parsed fields or None if parsing fails
        """
        if not line or line.strip() == '':
            return None
        
        match = self.pattern.match(line)
        
        if not match:
            return None
        
        data = match.groupdict()
        
        # Parse timestamp
        try:
            timestamp = self.parse_timestamp(data['timestamp'])
        except:
            return None
        
        # Parse size (handle '-' for 0)
        try:
            size = int(data['size']) if data['size'] != '-' else 0
        except:
            size = 0
        
        # Parse status code
        try:
            status = int(data['status'])
        except:
            return None
        
        return {
            'ip': data['ip'],
            'user': data['user'] if data['user'] != '-' else None,
            'timestamp': timestamp,
            'method': data['method'],
            'endpoint': data['endpoint'],
            'protocol': data['protocol'],
            'status': status,
            'size': size,
            'referrer': data['referrer'] if data['referrer'] != '-' else None,
            'user_agent': data['user_agent']
        }
    
    def parse_file(self, filepath: str, verbose: bool = True) -> pd.DataFrame:
        """
        Parse entire Nginx log file
        
        Args:
            filepath: Path to log file
            verbose: Print progress
            
        Returns:
            DataFrame with parsed logs
        """
        logs = []
        total_lines = 0
        parsed_count = 0
        
        if verbose:
            print(f"Parsing Nginx logs from: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    total_lines += 1
                    parsed = self.parse_line(line.strip())
                    if parsed:
                        logs.append(parsed)
                        parsed_count += 1
        except FileNotFoundError:
            if verbose:
                print(f"Error: File not found: {filepath}")
            return pd.DataFrame()
        
        if verbose:
            print(f"Parsing complete!")
            print(f"Total lines: {total_lines}")
            print(f"Successfully parsed: {parsed_count}")
            print(f"Invalid/skipped: {total_lines - parsed_count}")
        
        return pd.DataFrame(logs)


if __name__ == '__main__':
    # Test the parser
    parser = NginxLogParser()
    
    # Test line
    test_log = '192.168.1.100 - - [03/Mar/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "http://example.com" "Mozilla/5.0"'
    
    result = parser.parse_line(test_log)
    print("Test parse:")
    print(result)
