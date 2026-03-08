# KiranaConnect AWS Deployment Guide

## Recommended: EC2 Deployment (Quickest for Hackathon)

This deploys the full app on a single EC2 instance — same as running locally but accessible via a public URL.

---

## Step 1: Launch EC2 Instance

1. Go to **AWS Console** → **EC2** → **Launch Instance**
2. Configure:
   - **Name:** `kiranaconnect-server`
   - **AMI:** Ubuntu Server 24.04 LTS (Free tier eligible)
   - **Instance Type:** `t2.micro` (Free tier) or `t2.small` ($0.023/hr)
   - **Key Pair:** Create new → download `.pem` file (save it safely!)
   - **Security Group:** Allow these inbound rules:
     - SSH (port 22) — your IP
     - HTTP (port 80) — 0.0.0.0/0
     - Custom TCP (port 8000) — 0.0.0.0/0

3. Click **Launch Instance**
4. Copy the **Public IPv4 address** (e.g., `3.110.xxx.xxx`)

---

## Step 2: Connect to EC2 via SSH

Open PowerShell and run:

```powershell
# Navigate to where you downloaded the .pem key file
cd C:\Users\MASTER\Downloads

# Connect (replace with your key name and EC2 IP)
ssh -i "kiranaconnect-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

> **Windows tip:** If you get a permissions error, right-click the .pem file → Properties → Security → Advanced → Disable inheritance → Remove all users except your own account.

---

## Step 3: Install Dependencies on EC2

Once connected via SSH, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and pip
sudo apt install -y python3 python3-pip python3-venv git nginx

# Clone the repository
git clone -b dev-adarsh https://github.com/kmvenkatakrishna/medhira_ai_kirana_connect.git
cd medhira_ai_kirana_connect

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## Step 4: Test the Application

```bash
# Quick test — run directly
cd medhira_ai_kirana_connect
source venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open in your browser: `http://YOUR_EC2_PUBLIC_IP:8000/static/index.html`

If it works, press `Ctrl+C` to stop and proceed to the next step.

---

## Step 5: Set Up Nginx (Reverse Proxy)

This maps port 80 (standard HTTP) to your app on port 8000:

```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/kiranaconnect << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/kiranaconnect /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 6: Run as Background Service (Stays Running)

Create a systemd service so the app auto-starts and stays running:

```bash
sudo tee /etc/systemd/system/kiranaconnect.service << EOF
[Unit]
Description=KiranaConnect AI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/medhira_ai_kirana_connect
Environment=PATH=/home/ubuntu/medhira_ai_kirana_connect/venv/bin:/usr/bin
ExecStart=/home/ubuntu/medhira_ai_kirana_connect/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable kiranaconnect
sudo systemctl start kiranaconnect

# Check it's running
sudo systemctl status kiranaconnect
```

---

## Step 7: Verify Deployment

Open these URLs in your browser (replace with your EC2 IP):

```
http://YOUR_EC2_PUBLIC_IP/static/index.html          → Landing Page
http://YOUR_EC2_PUBLIC_IP/static/dashboard.html       → AI Dashboard
http://YOUR_EC2_PUBLIC_IP/static/chat.html            → AI Chat
http://YOUR_EC2_PUBLIC_IP/static/analytics.html       → Analytics
http://YOUR_EC2_PUBLIC_IP/static/orders.html          → Orders
http://YOUR_EC2_PUBLIC_IP/static/presentation.html    → PPT
http://YOUR_EC2_PUBLIC_IP/api/v1/health               → API Health
http://YOUR_EC2_PUBLIC_IP/api/v1/stores/S001/ai/insights → AI Test
```

---

## Useful Commands

```bash
# View logs
sudo journalctl -u kiranaconnect -f

# Restart after code changes
cd ~/medhira_ai_kirana_connect
git pull origin dev-adarsh
sudo systemctl restart kiranaconnect

# Stop
sudo systemctl stop kiranaconnect
```

---

## Cost Estimate (with $100 Credits)

| Resource | Cost |
|----------|------|
| t2.micro EC2 (free tier) | $0/month |
| t2.small EC2 (if needed) | ~$17/month |
| Data transfer | ~$1/month |
| **Total** | **$0–$18/month** |

Your $100 credits will last well beyond the hackathon evaluation period.

---

## Summary: Quick Deploy Cheat Sheet

```bash
# 1. SSH into EC2
ssh -i "key.pem" ubuntu@YOUR_IP

# 2. Clone & install
git clone -b dev-adarsh https://github.com/kmvenkatakrishna/medhira_ai_kirana_connect.git
cd medhira_ai_kirana_connect
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Setup nginx + systemd (copy commands from Steps 5 & 6)

# 4. Your live URL
# http://YOUR_EC2_PUBLIC_IP/static/index.html
```
