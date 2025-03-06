#/bin/sh
set -ex

cd ~/pirobot/pi
git pull
source ~/.venv/bin/activate
python3 -m hw_interface.main &
cd server && fastapi dev main.py --host 0.0.0.0
