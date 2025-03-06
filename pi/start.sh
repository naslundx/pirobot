#/bin/sh

set -ex

python3 -m hw_interface.main &
cd server && fastapi dev main.py --host 0.0.0.0
