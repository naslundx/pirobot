# Pi robot

## contact
ssh admin@192.168.50.254

## setup
```sh
sudo apt update
sudo apt upgrade
sudo apt install -y python3-picamzero python3-picamera2 libcap-dev

python3 -m venv --system-site-packages .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

# auto boot?
<!-- unclear start.sh -->
