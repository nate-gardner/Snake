# Initialize venv
if [ -d ".venv" ]; then
    python3 -m venv .venv
    ./.venv/bin/pip install pygame
fi
source .venv/bin/activate


python3 snake.py
deactivate