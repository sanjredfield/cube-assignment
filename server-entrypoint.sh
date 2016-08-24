/bin/bash wait-for-it/wait-for-it.sh video-postgres:5432
python manage.py migrate
python manage.py loaddata videolearner/fixtures/*.json
python manage.py runserver 0.0.0.0:8000
