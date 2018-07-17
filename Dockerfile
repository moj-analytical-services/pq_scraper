FROM python:3.7-alpine

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD pq_scraper.py .

ENTRYPOINT ["python3", "pq_scraper.py"]
