ARG DE_ECR

FROM ${DE_ECR}/python:3.7-alpine

ADD requirements.txt .
ADD pq_scraper.py .

RUN chmod -R 777 pq_scraper.py

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "pq_scraper.py"]


