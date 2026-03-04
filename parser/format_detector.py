"""
Log Format Auto-Detection - SOC-Lite
Automatically detects if logs are Apache or Nginx format
"""

import re
from typing import Literal


class FormatDetector:
    """Detect log format automatically"""
    
    # Sample patterns for each format
    APACHE_PATTERN = re.compile(
        r'^\S+\s+-\s+-\s+\[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4}\]\s+"[^"]+"\s+\d{3}'
    )
    
    NGINX_PATTERN = re.compile(
        r'^\S+\s+-\s+\S+\s+\[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4}\]\s+"[^"]+"\s+\d{3}'
    )
    
    @staticmethod
    def detect_format(filepath: str, sample_size: int = 10) -> Literal['apache', 'nginx', 'unknown']:
        """
        Detect log format by analyzing first few lines
        
        Args:
            filepath: Path to log file
            sample_size: Number of lines to sample
            
        Returns:
            'apache', 'nginx', or 'unknown'
        """
        apache_score = 0
        nginx_score = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= sample_size:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check Apache pattern
                    if FormatDetector.APACHE_PATTERN.match(line):
                        apache_score += 1
                    
                    # Check Nginx pattern
                    if FormatDetector.NGINX_PATTERN.match(line):
                        nginx_score += 1
                    
                    # Additional heuristics
                    # Apache typically has: ' - - ['
                    # Nginx can have: ' - user ['
                    if ' - - [' in line:
                        apache_score += 0.5
                    elif re.search(r' - \S+ \[', line) and ' - - [' not in line:
                        nginx_score += 0.5
        
        except FileNotFoundError:
            return 'unknown'
        
        # Determine format based on scores
        if apache_score > nginx_score:
            return 'apache'
        elif nginx_score > apache_score:
            return 'nginx'
        else:
            return 'unknown'
    
    @staticmethod
    def get_parser(filepath: str):
        """
        Get appropriate parser for the log file
        
        Args:
            filepath: Path to log file
            
        Returns:
            Parser instance (ApacheLogParser or NginxLogParser)
        """
        from parser.apache_parser import ApacheLogParser
        from parser.nginx_parser import NginxLogParser
        
        format_type = FormatDetector.detect_format(filepath)
        
        if format_type == 'apache':
            print(f"✅ Detected format: Apache")
            return ApacheLogParser()
        elif format_type == 'nginx':
            print(f"✅ Detected format: Nginx")
            return NginxLogParser()
        else:
            print(f"⚠️  Unknown format, defaulting to Apache")
            return ApacheLogParser()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python format_detector.py <logfile>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    format_type = FormatDetector.detect_format(filepath)
    print(f"Detected format: {format_type}")
