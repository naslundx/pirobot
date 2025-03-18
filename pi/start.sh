#/bin/sh
set -ex

cd ~/pirobot/pi
source ~/.venv/bin/activate
git stash
git pull
# pip install -r requirements.txt
# python3 -m hw_interface.main &
cd server && fastapi run main.py --host 0.0.0.0 --port 80
