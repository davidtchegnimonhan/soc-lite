"""Unit tests for Brute Force Detector"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from detection.brute_force_detector import detect_brute_force, get_summary, _severity

class TestBruteForceDetector:
    @pytest.fixture
    def sample_logs(self):
        now = datetime.now()
        data = []
        # Normal traffic
        for i in range(5):
            data.append({'ip': '10.0.0.1', 'timestamp': now + timedelta(seconds=i*10), 'status': 200, 'endpoint': '/home'})
        # Attack (15 attempts)
        for i in range(15):
            data.append({'ip': '203.0.113.50', 'timestamp': now + timedelta(seconds=i*10), 'status': 401, 'endpoint': '/login'})
        return pd.DataFrame(data)
    
    def test_detect_brute_force_attack(self, sample_logs):
        result = detect_brute_force(sample_logs, threshold=10)
        assert not result.empty
        assert len(result) == 1
        assert result.iloc[0]['ip'] == '203.0.113.50'
    
    def test_no_false_positives(self, sample_logs):
        normal = sample_logs[sample_logs['status'] == 200]
        result = detect_brute_force(normal, threshold=10)
        assert result.empty
    
    def test_severity_levels(self):
        assert _severity(5) == 'LOW'
        assert _severity(15) == 'MEDIUM'
        assert _severity(30) == 'HIGH'
        assert _severity(60) == 'CRITICAL'
