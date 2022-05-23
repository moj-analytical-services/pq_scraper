ARG DE_ECR
#FROM python:3.7-alpine
FROM ${DE_ECR}/python:3.9-slim

#WORKDIR /etl

ADD requirements.txt .
ADD pq_scraper.py .

RUN chmod -R 777 .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "pq_scraper.py"]
#ENTRYPOINT python python_scripts/$PYTHON_SCRIPT_NAME

