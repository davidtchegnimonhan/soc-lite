"""
Unit tests for Apache Log Parser
"""
import pytest
from datetime import datetime
from parser.apache_parser import ApacheLogParser


class TestApacheLogParser:
    """Test suite for ApacheLogParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return ApacheLogParser(log_format='combined')
    
    VALID_LOG = (
        '192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] '
        '"GET /admin HTTP/1.1" 401 1234 "http://example.com" "Mozilla/5.0"'
    )
    
    def test_parse_valid_log(self, parser):
        """Test parsing a valid log"""
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
        timestamp_str = '12/Feb/2026:10:30:45 +0000'
        result = parser.parse_timestamp(timestamp_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 12
    
    def test_parse_different_methods(self, parser):
        """Test parsing different HTTP methods"""
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        
        for method in methods:
            log = (
                f'192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] '
                f'"{method} /api/users HTTP/1.1" 200 500 "-" "-"'
            )
            result = parser.parse_line(log)
            assert result['method'] == method
    
    def test_parse_different_status_codes(self, parser):
        """Test parsing different HTTP status codes"""
        status_codes = [200, 301, 400, 401, 403, 404, 500]
        
        for status in status_codes:
            log = (
                f'192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] '
                f'"GET /test HTTP/1.1" {status} 100 "-" "-"'
            )
            result = parser.parse_line(log)
            assert result['status'] == status
    
    def test_parse_size_dash(self, parser):
        """Taille = - dans les logs"""
        log = '192.168.1.1 - - [12/Feb/2026:10:30:45 +0000] "GET /test HTTP/1.1" 200 - "-" "-"'
        result = parser.parse_line(log)
        assert result is not None
        assert result['size'] == 0
    
    def test_parse_returns_correct_types(self, parser):
        """Vérifier les types des champs"""
        log = '192.168.1.100 - - [12/Feb/2026:10:30:45 +0000] "GET /admin HTTP/1.1" 401 1234 "-" "Mozilla/5.0"'
        result = parser.parse_line(log)
        assert isinstance(result['ip'], str)
        assert isinstance(result['status'], int)
        assert isinstance(result['size'], int)
    
    def test_parse_file_returns_dataframe(self, parser):
        """parse_file retourne un DataFrame pandas"""
        import pandas as pd
        df = parser.parse_file('logs/sample.log', verbose=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_parse_file_has_correct_columns(self, parser):
        """Vérifier les colonnes du DataFrame"""
        df = parser.parse_file('logs/sample.log', verbose=False)
        for col in ['ip', 'timestamp', 'method', 'endpoint', 'status', 'size']:
            assert col in df.columns
    
    def test_parse_file_no_null_ips(self, parser):
        """Pas de valeurs nulles dans les IPs"""
        df = parser.parse_file('logs/sample.log', verbose=False)
        assert df['ip'].isnull().sum() == 0
