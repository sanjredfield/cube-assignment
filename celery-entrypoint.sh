/bin/bash wait-for-it/wait-for-it.sh video-postgres:5432
celery --app=cubeassignment.celeryapp worker --loglevel=INFO
