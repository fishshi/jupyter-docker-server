#!/bin/bash
set -e

apt-get update

apt-get install -y --no-install-recommends wget git
apt-get install -y --no-install-recommends cmake g++ build-essential libzmq3-dev libclang-dev clang llvm

apt-get clean && rm -rf /var/lib/apt/lists/*

conda install -y xeus-cling notebook -c conda-forge