#!/bin/bash

#only for 20.04 ubuntu

apt update
apt install -y dante-server libpam-pwdfile openssl curl git

ufw allow 1124/tcp

echo "Opened 1 server port:"
echo "1124"


ufw allow 1080/tcp
ufw allow 1101/tcp
ufw allow 1122/tcp
ufw allow 1212/tcp

echo "Opened 4 socks ports:"
echo "1080"
echo "1101"
echo "1122"
echo "1212"

echo "Installing JCL downloader..."
cd
git clone https://github.com/disiss/JCL_T1
cd JCL_T1

echo "Installing requirements..."
pip3 install -r requirements.txt
echo "Requirements in installed!"

# echo "Installing requirements..."
# python3 generate_proxies.py