#!/bin/bash
set -e

apt-get install -y --no-install-recommends libzmq3-dev

apt-get clean && rm -rf /var/lib/apt/lists/*

conda install -y xeus-cling -c conda-forge