
# virtual env:
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt

# running
fastapi dev server.py --host 0.0.0.0
