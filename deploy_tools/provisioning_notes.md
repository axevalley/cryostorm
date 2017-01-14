Provisioning a new site
=======================

## Required packages:

* nginx
* Python 3
* Git
* pip
* virtualenv

e.g.,, on Ubuntu:

    sudo apt-get install nginx git python3 python3-venv

## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME wit, e.g., staging.my-domain.com
*   sed "s/SITENAME/<sitename>/g" \
    deploy_tools/nginx.template.conf | sudo tee \
    /etc/nginx/sites-available/<sitename>
* enable site by symlinking config file to /etc/nginx/sites-enabled

## Systemd service

* see gunicorn-systemd.template.service
* replace SITENAME with, e.g., staging.my-domain.com
*   sed "s/SITENAME/<sitename>/g" \
    deploy_tools/gunicorn-systemd.template.service | sudo tee \
    /etc/systemd/system/gunicorn-<sitename>.service

## Restart Services

* sudo systemctl daemon-reload
* sudo systemctl reload nginx
* sudo systemctl enable gunicorn-<sitename>
* sudo systemctl start gunicorn-<sitename>

## Folder structure:
Assume we have a usser account ast /home/username

/home/username
|___sites
    |___SITENAME
        |___database
        |___source
        |___static
        |___virtualenv

## To Deply with fabric
fab deploy:host=<user>@<host>
