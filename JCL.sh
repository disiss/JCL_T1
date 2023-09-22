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
ExecStart=/root/JCL_T1/startup.sh start

[Install]
WantedBy=multi-user.target
EOF
}

apt update
apt install -y dante-server libpam-pwdfile openssl curl git python3-pip nodejs npm

npm sudo install pm2@latest -g

echo "Creating JCL_START_UP Service"
autostartup /etc/systemd/system/JCL_START_UP.service
systemctl enable JCL_START_UP
echo "${GREEN}JCL_START_UP Service is created!${NC}"

echo "Activating ufw"
ufw enable
echo "${GREEN}Ufw is activated!${NC}"

ufw allow 1124/tcp

echo "${GREEN}Opened 1 server port:${NC}"
echo "${RED}1124${NC}"

ufw allow 1080/tcp
ufw allow 1101/tcp
ufw allow 1122/tcp
ufw allow 1212/tcp

echo "${GREEN}Opened 4 socks ports:${NC}"
echo "${RED}1080"
echo "1101"
echo "1122"
echo "1212${NC}"

echo "${RED}Installing JCL...${NC}"
cd
git clone https://github.com/disiss/JCL_T1
wait
cd JCL_T1

echo "${RED}Installing requirements...${NC}"
pip3 install -r requirements.txt
echo "${GREEN}Requirements in installed!"
echo "JCL is succ installed!${NC}"

# echo "Installing requirements..."
# python3 generate_proxies.py