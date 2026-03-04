"""
Unit tests for Nginx Log Parser
"""

import pytest
from datetime import datetime
from parser.nginx_parser import NginxLogParser


class TestNginxLogParser:
    """Test suite for NginxLogParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return NginxLogParser(log_format='combined')
    
    VALID_LOG = (
        '192.168.1.100 - - [03/Mar/2026:10:30:45 +0000] '
        '"GET /admin HTTP/1.1" 401 1234 "http://example.com" "Mozilla/5.0"'
    )
    
    def test_parse_valid_log(self, parser):
        """Test parsing a valid Nginx log"""
        result = parser.parse_line(self.VALID_LOG)
        
        assert result is not None
        assert result['ip'] == '192.168.1.100'
        assert result['method'] == 'GET'
        assert result['endpoint'] == '/admin'
        assert result['status'] == 401
        assert result['size'] == 1234
    
    def test_parse_empty_log(self, parser):
        """Test parsing an empty log line"""
        result = parser.parse_line('')
        assert result is None
    
    def test_parse_malformed_log(self, parser):
        """Test parsing a malformed log line"""
        result = parser.parse_line('This is not a valid log')
        assert result is None
    
    def test_parse_timestamp(self, parser):
        """Test timestamp parsing"""
        timestamp_str = '03/Mar/2026:10:30:45 +0000'
        result = parser.parse_timestamp(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 3
        assert result.day == 3
    
    def test_parse_size_dash(self, parser):
        """Test parsing size field with dash"""
        log = (
            '192.168.1.100 - - [03/Mar/2026:10:30:45 +0000] '
            '"GET /admin HTTP/1.1" 401 - "http://example.com" "Mozilla/5.0"'
        )
        result = parser.parse_line(log)
        assert result['size'] == 0
    
    def test_parse_different_methods(self, parser):
        """Test parsing different HTTP methods"""
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        
        for method in methods:
            log = (
                f'192.168.1.100 - - [03/Mar/2026:10:30:45 +0000] '
                f'"{method} /api HTTP/1.1" 200 100 "-" "curl/7.0"'
            )
            result = parser.parse_line(log)
            assert result['method'] == method
