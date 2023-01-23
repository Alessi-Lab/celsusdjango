FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg > /dev/null
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7FCC7D46ACCC4CF8
RUN apt update
WORKDIR /app
RUN mkdir "/app/backup"
COPY . /app/
RUN pip install -r requirements.txt
RUN apt -y install postgresql-client-14
EXPOSE 8000
CMD ["gunicorn", "celsusdjango.wsgi:application", "--log-level=debug", "--timeout", "3600", "--bind", "0.0.0.0:8000"]