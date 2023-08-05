#!/usr/bin/env bash

set -e

# Gets the directory where this script is located
# Source: https://stackoverflow.com/a/246128/3760426
DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Where the Python virtual environment will be located
VENV_DIR="${DIR}/venv"

# Where are the cardsets located?
CARDSETS_DIR="${DIR}/PySolFC-Cardsets-2.1"

# Create python virtual environment if it does not exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating Python virtual environment in: ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
else
    echo "Python virtual environment already setup, skipping..."
fi

source "${VENV_DIR}/bin/activate"

echo "Installing Python dependencies..."
python3 -m pip install --disable-pip-version-check -r requirements.txt >/dev/null

if [ ! -d "${CARDSETS_DIR}" ]; then
    echo "Downloading and installing cardsets..."
    cd "${DIR}"
    bash "${DIR}/scripts/repack-min-cardsets.bash"
else
    echo "Cardsets already downloaded, skipping..."
fi

echo "Done!"
