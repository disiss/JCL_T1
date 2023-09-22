#!/bin/bash

sleep 2

cd
rm -rf JCL_T1
echo "JCL_T1 is delete"

echo "Downloading new version JCL_T1..."
git clone https://github.com/disiss/JCL_T1.git

echo "Starting JCL_T1..."
cd JCL_T1
bash JCL_start_after_update.sh