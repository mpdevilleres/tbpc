##Dockerizing Wagtail(Django) Boilerplate

###Specification
 - Docker
 - Docker-Compose
 - Django
 - Wagtail
 - Nginx
 - Postgresql

##Folder Structure

    Main
     |--- /nginx
     | |--- Dockerfile
     | |--- /logs    
     | |--- /ssl
     | |--- /sites-enabled
     | | |--- nginx_all
     | | |--- nginx_with_ssl
     | | |--- nginx_with_ssl_only
     | | |--- nginx_without_ssl     
     |--- /web
     | |--- Dockerfile
     | |--- manage.py
     | |--- requirements.txt
     | |--- /project
     | | |--- __init__.py
     | | |--- urls.py
     | | |--- wsgi.py
     | | |--- /settings
     | | |--- /templates 
     | | |--- /static
     | | |--- apps
     |--- .env
     |--- docker-compose.yml
     |--- README.md

###Install/Configure Docker
    $ sudo apt-get update
    $ sudo apt-get install curl
    $ sudo curl -sSL https://get.docker.com/ | sh

###Create ".env" file on the Main Folder - this file contains all OS level environment variables ()
    
    #sample .env file
    DEBUG=False
    TEMPLATE_DEBUG=False
    SECRET_KEY=yfehb3cr_(w9!&d&50f9n26^_je%4&eppxs1e2_@(*uof7nf-7
    DB_NAME=postgres
    DB_USER=postgres
    DB_PASS=postgres
    DB_SERVICE=postgres
    DB_PORT=5432
    THEME_VERSION=4.5.4
    

###Create SSL

    Soon
    
###Configuration

    # Change postgres password (Security Reasons), Add User for the application
    $ psql -h 127.0.0.1 -p 5432 -U postgres --password
    postgres=# ALTER USER postgres WITH PASSWORD 'desired_password';
               CREATE DATABASE web;
               CREATE USER web WITH PASSWORD 'test';
               GRANT ALL PRIVILEGES ON DATABASE "web" to web;

    $ docker-compose run web python manage.py migrate

###Postgres Backup

    $ docker exec -it suite_postgres_1 \
      sh -c "pg_dump -U postgres_user postgres_dbname | gzip > /postgres/backup/dump_`date +%d-%m-%Y"_"%H_%M_%S`.gz"

###Postgres Restore

    $ docker exec -it suite_postgres_1 \
        sh -c "gunzip -c /postgres/backup/filename.gz | psql -U postgres_user postgres_dbname"

###Execute Raw sql with django
    from django.db import connection
    cursor = connection.cursor()

    cursor.execute("ALTER SEQUENCE team_tasks_id_seq RESTART WITH 2001;")
    # Passing parameters don't use raw string use [] for security
    cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])    



###Handy Snippets

- KILL ALL DOCKER CONTAINER


    $ docker kill $(docker ps -a -q)

- REMOVE ALL DOCKER CONTAINER


    $ docker rm $(docker ps -a -q)

- LIST ACTIVE SERVICES


    $ netstat -tuplen

###Deployment Note
    git clone -b <branch> <repo> <foldername>
    copy .env to the Host
    copy SSL Certs
    copy static files
    update DB

