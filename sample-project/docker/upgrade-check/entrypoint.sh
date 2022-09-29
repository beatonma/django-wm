echo "Installing previous django-wm..."
pip install django-wm[celery]==2.3.0
echo "[OK] previous django-wm installed."

echo "Setting up old server..."
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput || true
python manage.py collectstatic --noinput
echo "[OK] Old server setup."

echo "Creating sample webmention data..."
python manage.py create_sample_webmentions
echo "[OK] Created sample webmention data."

echo "Upgrading django-wm to latest pre-release..."
pip install --pre --upgrade django-wm[celery]
echo "[OK] Upgraded django-wm to latest pre-release."

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

celery -A sample_project worker -E &

python manage.py selfcheck &
echo "New server starting..."
python manage.py runserver 0.0.0.0:80 --noreload
