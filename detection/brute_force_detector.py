"""
Brute Force Attack Detector - SOC-Lite

Algorithm: Sliding Window
- Group failed auth (401/403) by IP
- 5-minute sliding window
- >10 failures = attack flagged
"""

import pandas as pd
from datetime import timedelta
from typing import List, Optional


def detect_brute_force(
    df: pd.DataFrame,
    window_minutes: int = 5,
    threshold: int = 10,
    whitelist: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Detect brute force attacks in parsed Apache logs.

    Args:
        df: Parsed log DataFrame
        window_minutes: Sliding window size in minutes
        threshold: Failed attempts to trigger alert
        whitelist: IPs to ignore

    Returns:
        DataFrame with detected attacks
    """
    if df.empty:
        return pd.DataFrame()

    # Apply whitelist
    if whitelist:
        df = df[~df['ip'].isin(whitelist)]

    # Filter failed auth attempts
    failed = df[df['status'].isin([401, 403])].copy()

    if failed.empty:
        print("✅ No failed auth attempts found")
        return pd.DataFrame()

    failed = failed.sort_values('timestamp')
    window = timedelta(minutes=window_minutes)
    attacks = []

    for ip, group in failed.groupby('ip'):
        timestamps = [t for t in group['timestamp'].tolist() if t is not None]

        for i, start_time in enumerate(timestamps):
            window_hits = [t for t in timestamps[i:] if t <= start_time + window]

            if len(window_hits) >= threshold:
                attacks.append({
                    'ip': ip,
                    'attempts': len(window_hits),
                    'first_seen': start_time,
                    'last_seen': max(window_hits),
                    'endpoints': ', '.join(group['endpoint'].unique()[:3]),
                    'severity': _severity(len(window_hits))
                })
                break

    if not attacks:
        print("✅ No brute force attacks detected")
        return pd.DataFrame()

    result = pd.DataFrame(attacks).sort_values('attempts', ascending=False)
    print(f"🚨 Detected {len(attacks)} attack(s)")
    return result


def _severity(attempts: int) -> str:
    """Classify attack severity"""
    if attempts >= 50: return 'CRITICAL'
    if attempts >= 25: return 'HIGH'
    if attempts >= 10: return 'MEDIUM'
    return 'LOW'


def get_summary(attacks_df: pd.DataFrame) -> dict:
    """Summary statistics of detected attacks"""
    if attacks_df.empty:
        return {'total_attacks': 0}

    return {
        'total_attacks': len(attacks_df),
        'critical': len(attacks_df[attacks_df['severity'] == 'CRITICAL']),
        'high':     len(attacks_df[attacks_df['severity'] == 'HIGH']),
        'medium':   len(attacks_df[attacks_df['severity'] == 'MEDIUM']),
        'top_attacker': attacks_df.iloc[0]['ip'],
        'max_attempts': int(attacks_df['attempts'].max())
    }
