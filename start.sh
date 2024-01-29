source .venv/bin/activate
uvicorn config.asgi:application --host 0.0.0.0 --port 9002 --reload
