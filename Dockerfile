FROM python:3-alpine

WORKDIR /app
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . .

EXPOSE 5000
CMD ["python", "m.py"]