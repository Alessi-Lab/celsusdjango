# Celsus-Django
Back-end architecture for Celsus and Curtain web applications.

## Installation instructions
The first step for installation is downloading the content of the following github repoes
1. https://github.com/noatgnu/netphos-web (wrapper for web usage of NetPhos 3.1)
2. https://github.com/noatgnu/celsusdjango (this repository)

Then, download NetPhos 3.1 linux version from this link https://services.healthtech.dtu.dk/service.php?NetPhos-3.1 and copy it into the location where the netphos-web repo had been downloaded.

The simplest method for installation of Celsus-Django is through `docker-compose`. In order to use docker please ensure that you have docker and docker-compose installed.

Copy and paste the content of the following `docker-compose.yml` file into the location where you want to store the backend application.

```yaml
version: "3.8"
services:
  db:
    image: postgres
    volumes:
      - ./data/db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    container_name: db
    networks:
      - celsus-net
  web:
    container_name: web
    build:
      context: .
      dockerfile: ./docker/Dockerfile
    command: gunicorn celsusdjango.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      - WORKDB_PROFILE=production
      - SECRET_KEY=
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_HOST=db
      - DJANGO_CORS_WHITELIST=
      - DJANGO_ALLOWED_HOSTS=
      - DJANGO_MEDIA_ROOT=/app/media/
      - ORCID_OAUTH_CLIENT_ID=
      - ORCID_OAUTH_SECRET=
      - CURTAIN_ALLOW_NON_STAFF_DELETE=0
      - CURTAIN_ALLOW_NON_USER_POST=1
    depends_on:
      - db
    volumes:
      - ./data/media:/app/media
    networks:
      - celsus-net
  netphos:
    build:
      context: /usr/path/to/netphos/web/git/clone
      dockerfile: /usr/path/to/netphos/web/git/clone/Dockerfile
    container_name: netphos
    networks:
      - celsus-net
networks:
  celsus-net:
```

Replace environmental variables in the docker-compose file content with the appropriate value for applications where
1. `SECRET_KEY` is your DJANGO secret key.
2. `DJANGO_CORS_WHITELIST` is a list of frontend url that are allowed to access our backend delimited by commas
3. `DJANGO_ALLOWED_HOSTS` is a list of hostname that can be used to access our backend
4. `ORCID_OAUTH_CLIENT_ID` is your application clientid registered from orcid.org
5. `ORCID_OAUTH_SECRET` is your application secret registered from orcid.org
6. `CURTAIN_ALLOW_NON_STAFF_DELETE` value `1` or `0` is to whether or not allow non_staff Curtain user to delete a Curtain entry.
7. `CURTAIN_ALLOW_NON_USER_POST` value `1` or `0` is to whether or not allow not yet authenticated user to save a new Curtain session.


From the location of the `docker-compose.yml` file, execute

```shell
docker-compose up -d
```

Then execute the following command to perform initial database tables creation in django

```shell
docker-compose exec -it web python manage.py migrate
```

The following commands to download the initial fixtures for disease and taxonomy data and add them into our data table. These are optional and only if you are running Celsus data management application.

```shell
docker-compose exec -it web curl -o /app/celsus/fixtures/diseases.json https://nextcloud1.muttsu.xyz/s/dBnT8tGxjneB4AR/download/diseases.json
docker-compose exec -it web curl -o /app/celsus/fixtures/organisms.json https://nextcloud1.muttsu.xyz/s/saKLFYRj4RqXaDa/download/organisms.json
docker-compose exec -it web python manage.py loaddata diseases.json
docker-compose exec -it web python manage.py loaddata organisms.json
```

Then create your admin account

```shell
docker-compose exec -it web python manage.py createsuperuser
```

Then, visit `https://orcid.org/developer-tools` with your login information and enable public api and enter the uri of the frontend you want to access the data.