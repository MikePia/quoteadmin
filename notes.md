* sudo apt-get update
* sudo apt-get upgrade
* sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install django
pip install gunicorn
sudo apt-get install -y nginx
gunicorn -bind 0.0.0.0:8000 aooo.wsgi:application {to view the running app}

sudo apt-get install supervisor
cd /et/supervosor/conf.d
sudo touch gunicorn.conf
data to enter -

[program.gunicorn]
directory=/home/ubuntu/resume/djangoResume
command = {path}/venv/bin/gunicorn -workers 3 -bind
unix:/home/ubuntyu/resume/app.sock djangoResume.wsgi:applictation