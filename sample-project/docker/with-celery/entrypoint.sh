#!/bin/ash
echo "Setting up server..."

python manage.py migrate
echo "- Migrations complete"
python manage.py createsuperuser --noinput || true
echo "- Superuser ready"
python manage.py collectstatic --noinput
echo "- Static files collected"

python manage.py sample_app_init

echo "Starting server..."
python manage.py runserver 0.0.0.0:80 --noreload
