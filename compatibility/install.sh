#!/bin/bash

OS=$(uname)

if [[ "$OS" == "Linux" ]]; then
    pip install -r requirements/requirements-linux.txt
elif [[ "$OS" == "Darwin" ]]; then
    pip install -r requirements/requirements-mac.txt
elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* ]]; then
    pip install -r requirements/requirements-win.txt
else
    echo "Unsupported system"
    exit 1
fi