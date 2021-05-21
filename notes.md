# Did these top to bottom and failed
* sudo apt-get update
* sudo apt-get upgrade
* sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install django
pip install gunicorn
sudo apt-get install -y nginx
gunicorn -bind 0.0.0.0:8000 quotad.wsgi:application {to view the running app}

sudo apt-get install supervisor
cd /et/supervosor/conf.d
sudo touch gunicorn.conf
# data to enter -
```conf
[program.gunicorn]
directory=/home/ubuntu/resume/djangoResume
command = {path}/venv/bin/gunicorn -workers 3 -bind
unix:/home/ubuntu/resume/app.sock djangoResume.wsgi:applictation

autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn.err.log
stdout_logfile=/var/log/gunicorn.out.log

[group:guni]
program:gunicorn
#### Note that the tut had programs:gunicorn -- think program:gunicorn -- matching top heading is correct
##### end data
```
sudo mkdir /var/log/gunicorn
sudo supervisorctl update
sudo supervisorctl reread

cd /etc/nginx/sites-available
sudo touch django.conf
# Paste following code

```conf
server {
    server_name 18.116.230.127;
    servername ec2-18-116-230-127.us-east-2.compute.amazonaws.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/usr/local/quoteadmin/app.sock;
    }

    location / static {
        autoindex on;
        alias /usr/local/quoteadmin/quotad/static/;
    }
    location /media/ {
        autoindex on;
        alias /usr/local/quoteadmin/quotad/media;
    }
}
```

sudo ln django.conf /etc/nginx/sites-enabled/
sudo nginx -t
### went outside the line here
* edit nginx.conf to increase bucket size same as tut
* nginx -t worked same as tutorial
* re did:
    * sudo supervisorctl reload
    * sudo service nginx restart
    * sudo supervisorctl reload
    And its up

### For SSL
https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx

* To allow big size data make changes to nginx files by adding client_max_body_size 100M

### psql to connect to remote db

$ sudo ufw allow 5432/tcp
$ sudo systemctl restart postgresql
sudo su - postgres
$ psql -h database-1.cilvogad6ynt.us-east-2.rds.amazonaws.com -d  quotedb  -U quotedbuser 
quotedb=> select count(*) from allquotes;
