# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "taxi_app_backend"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None 