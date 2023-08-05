#!/usr/bin/env bash

set -e

# Gets the directory where this script is located
# Source: https://stackoverflow.com/a/246128/3760426
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Where the Python virtual environment will be located
VENV_DIR="${DIR}/venv"

# Create python virtual environment if it does not exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "Please run \"./setup.sh\" script first!"
    exit 1
fi

source "${VENV_DIR}/bin/activate"

cd "${DIR}"
python3 pysol.py
