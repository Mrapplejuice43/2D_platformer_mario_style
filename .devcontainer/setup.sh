#!/usr/bin/env bash
set -eux

curl -LsSf https://astral.sh/uv/install.sh | sh
sudo cp -v ./.devcontainer/asound.conf /etc/asound.conf
sudo usermod -aG audio vscode
sudo setfacl -m u:vscode:rw /dev/snd/* 