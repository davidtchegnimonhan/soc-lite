# SOC-Lite Installation Guide

## Prerequisites

- Python 3.8 or higher
- 512MB RAM minimum
- 1GB disk space
- Linux/macOS/Windows with WSL2

## Method 1: Docker (Easiest)

### Requirements
- Docker 20.10+
- Docker Compose 1.29+

### Steps

1. **Clone repository**
```bash
git clone https://github.com/davidtchegnimonhan/soc-lite.git
cd soc-lite
```

2. **Start services**
```bash
docker-compose up -d
```

3. **Verify**
```bash
docker ps
# Should show soc-lite-dashboard running
```

4. **Access**
Open http://localhost:5000

### Troubleshooting Docker

**Port already in use:**
```bash
# Edit docker-compose.yml, change port
ports:
  - "8080:5000"  # Use 8080 instead
```

**Container won't start:**
```bash
# Check logs
docker-compose logs -f
```

## Method 2: Python (Native)

### Ubuntu/Debian
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Clone
git clone https://github.com/davidtchegnimonhan/soc-lite.git
cd soc-lite

# Setup virtualenv
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run
python dashboard/app.py
```

### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip git
# Then follow Ubuntu steps above
```

### macOS
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3 git

# Then follow Ubuntu steps above
```

### Windows (WSL2)
```bash
# Enable WSL2
wsl --install

# Inside WSL2, follow Ubuntu steps
```

## Method 3: Automated Script
```bash
curl -sSL https://raw.githubusercontent.com/davidtchegnimonhan/soc-lite/main/install.sh | bash
```

## Verifying Installation
```bash
# Activate venv
source venv/bin/activate

# Run tests
pytest tests/ -v

# Should show: 14 tests passing
```

## Using with Real Logs

### Apache
```bash
# Point to your Apache logs
python main.py --log /var/log/apache2/access.log

# Or with Docker
docker run -d \
  -p 5000:5000 \
  -v /var/log/apache2:/app/logs:ro \
  soc-lite:latest
```

### Nginx (Coming Soon)

Support for Nginx logs in v1.0

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Nginx reverse proxy
- SSL certificates
- Systemd service
- High availability setup

## Getting Help

- 📖 [Documentation](https://github.com/davidtchegnimonhan/soc-lite/wiki)
- 🐛 [Issues](https://github.com/davidtchegnimonhan/soc-lite/issues)
- 📧 Email: david.tchegnimonhan@example.com
