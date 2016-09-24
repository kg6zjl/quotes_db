sudo yum -y update

git init
git reset --hard
git fetch https://github.com/steve-smp/quotes_db.git
git pull https://github.com/steve-smp/quotes_db.git

sudo pip install -r requirements.txt

kill $(ps aux | grep '[g]unicorn' | awk '{print $2}')

sudo /etc/init.d/nginx restart

gunicorn --bind 0.0.0.0:5000 --workers 16 wsgi &
