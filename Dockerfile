# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-libmysqlclient-dev gcc libgl1 \
 libgl1-mesa-glx \ 
 libglib2.0-0 \
 libsm6 \
 libxrender1 \
 libxext6
 
RUN pip3 install -r requirements.txt

COPY . .

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# configure the container to run in an executed manner
ENTRYPOINT ["python"]

CMD ["app.py"]