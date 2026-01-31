#!/usr/bin/env bash
set -eux

sudo cp -v ./.devcontainer/asound.conf /etc/asound.conf
sudo usermod -aG audio vscode
sudo usermod -aG pulse-access vscode
sudo usermod -aG audio pulse
sudo usermod -aG pulse-access root
sudo setfacl -m u:vscode:rw /dev/snd/* 
curl -LsSf https://astral.sh/uv/install.sh | sh