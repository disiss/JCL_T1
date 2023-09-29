#!/bin/bash

#only for 20.04 ubuntu

GREEN=$'\e[0;32m'
RED=$'\e[0;31m'
NC=$'\e[0m'

function autostartup() {
cat > "$1" <<EOF
[Unit]
Description=JCL START UP SERVICE

[Service]
Type=simple
WorkingDirectory=/root/JCL_T1
ExecStart=/usr/bin/python3 /root/JCL_T1/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
}

apt update
apt install -y dante-server libpam-pwdfile openssl curl git python3-pip nodejs sysstat net-tools

echo "Creating JCL_START_UP Service"
autostartup /etc/systemd/system/JCL_START_UP.service
systemctl enable JCL_START_UP
echo "${GREEN}JCL_START_UP Service is created!${NC}"

echo "Activating ufw"
ufw --force enable
echo "${GREEN}Ufw is activated!${NC}"

ufw allow 22

ufw allow 1124/tcp
ufw allow 3000/tcp

echo "${GREEN}Opened 2 server ports:${NC}"
echo "${RED}1124${NC}"
echo "${RED}3000${NC}"

ufw allow 1080/tcp
ufw allow 1101/tcp
ufw allow 1122/tcp
ufw allow 1212/tcp

echo "${GREEN}Opened 4 socks ports:${NC}"
echo "${RED}1080"
echo "1101"
echo "1122"
echo "1212${NC}"

systemctl disable danted

echo "${RED}Installing JCL...${NC}"
cd
git clone https://github.com/disiss/JCL_T1
wait
cd JCL_T1

echo "${RED}Installing requirements...${NC}"
pip3 install -r requirements.txt
echo "${GREEN}Requirements in installed!${NC}"

npm install -g pm2

cd http_proxy_server
pm2 start main.js

cd
cd api_server
pm2 start app.js

cd
cd JCL_T1

pm2 save
pm2 startup

mkdir proxies_config
cd proxies_config

mkdir socks5
mkdir http

cd
cd JCL_T1

# echo "${GREEN}Start Generating Proxies!${NC}"
# python3 generate_proxies.py

echo "${GREEN}JCL is succ installed!${NC}"