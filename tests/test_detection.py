"""
Unit tests for Brute Force Detector
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from detection.brute_force_detector import detect_brute_force, get_summary, _severity


class TestBruteForceDetector:
    """Test suite for brute force detection"""
    
    @pytest.fixture
    def sample_logs(self):
        """Create sample log DataFrame"""
        now = datetime.now()
        data = []
        
        # Normal traffic
        for i in range(5):
            data.append({
                'ip': '10.0.0.1',
                'timestamp': now + timedelta(seconds=i*10),
                'status': 200,
                'endpoint': '/home'
            })
        
        # Brute force attack (15 attempts in 3 minutes)
        for i in range(15):
            data.append({
                'ip': '203.0.113.50',
                'timestamp': now + timedelta(seconds=i*10),
                'status': 401,
                'endpoint': '/login'
            })
        
        return pd.DataFrame(data)
    
    def test_detect_no_attacks_on_normal_traffic(self, sample_logs):
        """Should not detect attacks in normal traffic"""
        normal = sample_logs[sample_logs['status'] == 200]
        result = detect_brute_force(normal, threshold=10)
        assert result.empty
    
    def test_detect_brute_force_attack(self, sample_logs):
        """Should detect brute force attack"""
        result = detect_brute_force(sample_logs, threshold=10)
        assert not result.empty
        assert len(result) == 1
        assert result.iloc[0]['ip'] == '203.0.113.50'
        assert result.iloc[0]['attempts'] >= 10
    
    def test_threshold_affects_detection(self, sample_logs):
        """Different thresholds should affect detection"""
        result_low = detect_brute_force(sample_logs, threshold=5)
        result_high = detect_brute_force(sample_logs, threshold=20)
        
        assert len(result_low) >= len(result_high)
    
    def test_whitelist_ignores_ips(self, sample_logs):
        """Whitelisted IPs should be ignored"""
        result = detect_brute_force(sample_logs, threshold=10, whitelist=['203.0.113.50'])
        assert result.empty
    
    def test_empty_dataframe(self):
        """Should handle empty DataFrame"""
        empty_df = pd.DataFrame()
        result = detect_brute_force(empty_df)
        assert result.empty
    
    def test_no_failed_auth(self):
        """Should handle logs with no failed auth"""
        data = [{
            'ip': '10.0.0.1',
            'timestamp': datetime.now(),
            'status': 200,
            'endpoint': '/home'
        }]
        df = pd.DataFrame(data)
        result = detect_brute_force(df)
        assert result.empty
    
    def test_severity_classification(self):
        """Test severity levels"""
        assert _severity(5) == 'LOW'
        assert _severity(15) == 'MEDIUM'
        assert _severity(30) == 'HIGH'
        assert _severity(60) == 'CRITICAL'
    
    def test_get_summary_empty(self):
        """Summary of empty DataFrame"""
        empty_df = pd.DataFrame()
        summary = get_summary(empty_df)
        assert summary['total_attacks'] == 0
    
    def test_get_summary_with_attacks(self, sample_logs):
        """Summary should include attack stats"""
        result = detect_brute_force(sample_logs, threshold=10)
        summary = get_summary(result)
        
        assert summary['total_attacks'] == 1
        assert 'top_attacker' in summary
        assert 'max_attempts' in summary
        assert summary['top_attacker'] == '203.0.113.50'
