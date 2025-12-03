#!/bin/bash
set -e

apt-get install -y --no-install-recommends openjdk-21-jre
mkdir jjava
wget https://github.com/dflib/jjava/releases/download/1.0-a6/jjava-1.0-a6-kernelspec.zip
unzip jjava-1.0-a6-kernelspec.zip -d jjava
rm jjava-1.0-a6-kernelspec.zip
jupyter kernelspec install jjava --name=java --sys-prefix
rm -rf jjava