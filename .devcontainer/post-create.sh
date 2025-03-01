#!/usr/bin/env bash

mkdir -p /workspaces/exoconv/.vscode
cp /workspaces/exoconv/.devcontainer/vscode/* /workspaces/exoconv/.vscode

make bootstrap
