kill $(ps aux | grep '[g]unicorn' | awk '{print $2}')

sudo /etc/init.d/nginx restart

gunicorn --bind 0.0.0.0:5000 --workers 16 wsgi &