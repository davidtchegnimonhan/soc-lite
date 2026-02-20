"""
Attack Injector - Generate logs with realistic attack patterns

Creates synthetic Apache logs with:
- Normal traffic (baseline)
- Brute force attacks (multiple IPs)
- Port scans (enumeration)
- Mixed scenarios
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple


class AttackInjector:
    """Inject attack patterns into Apache logs"""
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.logs = []
        
        # IP pools
        self.normal_ips = [f"10.0.{random.randint(1,50)}.{random.randint(1,255)}" for _ in range(20)]
        self.attacker_ips = [f"203.0.113.{i}" for i in range(10, 20)]  # Suspicious range
        
        # Endpoints
        self.normal_endpoints = ["/", "/about", "/contact", "/products", "/static/main.css"]
        self.auth_endpoints = ["/login", "/admin", "/wp-admin", "/administrator"]
        self.scan_endpoints = [
            "/phpmyadmin", "/admin", "/.env", "/config.php", "/backup.sql",
            "/test.php", "/shell.php", "/upload.php", "/wordpress/wp-admin",
            "/.git/config", "/api/v1/users", "/api/v2/admin"
        ]
    
    def generate_normal_traffic(self, num_logs: int, start_time: datetime) -> List[str]:
        """Generate normal user traffic"""
        logs = []
        statuses = [200] * 80 + [404] * 15 + [301] * 5  # Realistic distribution
        
        for i in range(num_logs):
            ip = random.choice(self.normal_ips)
            ts = (start_time + timedelta(seconds=i * random.randint(1, 10))).strftime("%d/%b/%Y:%H:%M:%S +0000")
            method = "GET"
            endpoint = random.choice(self.normal_endpoints)
            status = random.choice(statuses)
            size = random.randint(500, 8000)
            
            log = f'{ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "Mozilla/5.0"\n'
            logs.append(log)
        
        return logs
    
    def inject_brute_force(self, attacker_ip: str, start_time: datetime, num_attempts: int = 50) -> Tuple[List[str], dict]:
        """Inject a brute force attack from one IP"""
        logs = []
        ground_truth = {
            'type': 'brute_force',
            'ip': attacker_ip,
            'attempts': num_attempts,
            'start_time': start_time,
            'endpoints': []
        }
        
        for i in range(num_attempts):
            ts = (start_time + timedelta(seconds=i * random.randint(2, 8))).strftime("%d/%b/%Y:%H:%M:%S +0000")
            method = "POST"
            endpoint = random.choice(self.auth_endpoints)
            status = 401 if i < num_attempts - 1 else 200  # Last attempt succeeds
            size = random.randint(200, 500)
            
            log = f'{attacker_ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "Python/3.9"\n'
            logs.append(log)
            
            if endpoint not in ground_truth['endpoints']:
                ground_truth['endpoints'].append(endpoint)
        
        ground_truth['end_time'] = start_time + timedelta(seconds=(num_attempts - 1) * 8)
        return logs, ground_truth
    
    def inject_port_scan(self, attacker_ip: str, start_time: datetime, num_attempts: int = 30) -> Tuple[List[str], dict]:
        """Inject a port scan / enumeration attack"""
        logs = []
        ground_truth = {
            'type': 'port_scan',
            'ip': attacker_ip,
            'attempts': num_attempts,
            'start_time': start_time,
            'endpoints': []
        }
        
        for i in range(num_attempts):
            ts = (start_time + timedelta(seconds=i * 2)).strftime("%d/%b/%Y:%H:%M:%S +0000")
            method = "GET"
            endpoint = random.choice(self.scan_endpoints)
            status = random.choice([404, 403, 404, 404])  # Mostly not found
            size = random.randint(150, 400)
            
            log = f'{attacker_ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "curl/7.68.0"\n'
            logs.append(log)
            ground_truth['endpoints'].append(endpoint)
        
        ground_truth['end_time'] = start_time + timedelta(seconds=(num_attempts - 1) * 2)
        return logs, ground_truth
    
    def generate_mixed_scenario(self, num_normal: int = 5000, num_attacks: int = 5) -> dict:
        """Generate a realistic mixed scenario"""
        start_time = datetime.now() - timedelta(hours=6)
        all_logs = []
        ground_truth_attacks = []
        
        print(f"🔨 Generating mixed scenario...")
        print(f"   Normal traffic: {num_normal} logs")
        print(f"   Attacks: {num_attacks}")
        
        # Generate normal traffic
        normal_logs = self.generate_normal_traffic(num_normal, start_time)
        all_logs.extend(normal_logs)
        
        # Inject brute force attacks
        for i in range(num_attacks // 2):
            attacker_ip = self.attacker_ips[i]
            attack_start = start_time + timedelta(hours=i + 1)
            attack_logs, attack_info = self.inject_brute_force(
                attacker_ip, 
                attack_start, 
                num_attempts=random.randint(15, 60)
            )
            all_logs.extend(attack_logs)
            ground_truth_attacks.append(attack_info)
        
        # Inject port scans
        for i in range(num_attacks // 2, num_attacks):
            attacker_ip = self.attacker_ips[i]
            attack_start = start_time + timedelta(hours=i + 1)
            attack_logs, attack_info = self.inject_port_scan(
                attacker_ip,
                attack_start,
                num_attempts=random.randint(20, 40)
            )
            all_logs.extend(attack_logs)
            ground_truth_attacks.append(attack_info)
        
        # Shuffle to make it realistic
        random.shuffle(all_logs)
        
        # Write to file
        with open(self.output_file, 'w') as f:
            f.writelines(all_logs)
        
        print(f"✅ Generated {len(all_logs)} logs → {self.output_file}")
        print(f"   Ground truth: {len(ground_truth_attacks)} attacks injected")
        
        return {
            'total_logs': len(all_logs),
            'normal_logs': num_normal,
            'attack_logs': len(all_logs) - num_normal,
            'attacks': ground_truth_attacks
        }


if __name__ == '__main__':
    import json
    
    # Generate test dataset
    injector = AttackInjector('data/attack_dataset.log')
    metadata = injector.generate_mixed_scenario(num_normal=5000, num_attacks=5)
    
    # Save ground truth
    with open('data/attack_ground_truth.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print("\n📊 Summary:")
    print(f"   Total logs: {metadata['total_logs']}")
    print(f"   Attacks injected: {len(metadata['attacks'])}")
    print("   Ground truth saved: data/attack_ground_truth.json")
