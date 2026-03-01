web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn presentpickz.wsgi --workers 3 --threads 2 --timeout 60 --keep-alive 5
