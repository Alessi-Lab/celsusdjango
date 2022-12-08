FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app/
RUN ls
RUN curl -o /app/celsus/fixtures/diseases.json https://nextcloud1.muttsu.xyz/s/dBnT8tGxjneB4AR/download/diseases.json
RUN curl -o /app/celsus/fixtures/organisms.json https://nextcloud1.muttsu.xyz/s/saKLFYRj4RqXaDa/download/organisms.json
RUN pip install -r requirements.txt