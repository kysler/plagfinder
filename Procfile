web: flask db upgrade; gunicorn -w 4 "app:create_app()"
worker: python worker.py
