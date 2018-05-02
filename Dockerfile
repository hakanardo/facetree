FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /app/

RUN apt-get install zlib1g-dev
RUN pip3 install --no-cache-dir -r requirements.txt
