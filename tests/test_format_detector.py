"""
Unit tests for Format Detector
"""

import pytest
import tempfile
import os
from parser.format_detector import FormatDetector


class TestFormatDetector:
    """Test suite for FormatDetector"""
    
    def test_detect_apache_format(self):
        """Test detection of Apache format"""
        # Create temp file with Apache logs
        apache_logs = [
            '192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "-" "Mozilla/5.0"',
            '192.168.1.101 - - [12/Feb/2026:10:30:46 +0000] "POST /login HTTP/1.1" 200 500 "-" "curl/7.0"',
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write('\n'.join(apache_logs))
            temp_path = f.name
        
        try:
            result = FormatDetector.detect_format(temp_path)
            assert result == 'apache'
        finally:
            os.unlink(temp_path)
    
    def test_detect_nginx_format(self):
        """Test detection of Nginx format"""
        # Create temp file with Nginx logs
        nginx_logs = [
            '192.168.1.100 - user1 [03/Mar/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "http://example.com" "Mozilla/5.0"',
            '192.168.1.101 - user2 [03/Mar/2026:10:30:46 +0000] "POST /api HTTP/1.1" 200 500 "-" "curl/7.0"',
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write('\n'.join(nginx_logs))
            temp_path = f.name
        
        try:
            result = FormatDetector.detect_format(temp_path)
            assert result == 'nginx'
        finally:
            os.unlink(temp_path)
    
    def test_get_parser_apache(self):
        """Test getting Apache parser"""
        apache_logs = [
            '192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "-" "Mozilla/5.0"',
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write('\n'.join(apache_logs))
            temp_path = f.name
        
        try:
            parser = FormatDetector.get_parser(temp_path)
            from parser.apache_parser import ApacheLogParser
            assert isinstance(parser, ApacheLogParser)
        finally:
            os.unlink(temp_path)
