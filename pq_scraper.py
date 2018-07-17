from urllib.parse import urlencode
import json
import os
import sys

import boto3
import requests


API_URL = "https://lda.data.parliament.uk/answeredquestions.json"


def _get_response_json(url):
    response = requests.get(url)
    if not response.ok:
        raise Exception(
            f"Request to '{url}' failed: Response status code = '{response.status_code}': Response body = '{response.text}'"
        )

    return response.json()


def _next_url(json):
    if "next" in json["result"]:
        return json["result"]["next"]

    return None


def _result_pages(date, page_size):
    PARAMS = {
        "min-date": date,
        "max-date": date,
        "_pageSize": page_size,
        "_sort": "uin",
    }

    url = f"{API_URL}?{urlencode(PARAMS)}"
    json = _get_response_json(url)

    yield json["result"]["items"]  # First page

    while _next_url(json):  # Subsequent pages (if any)
        url = _next_url(json) + f"&_pageSize={page_size}"
        json = _get_response_json(url)
        yield json["result"]["items"]


def get_questions(date, page_size=200):
    questions = []
    for page_items in _result_pages(date=date, page_size=page_size):
        questions.extend(page_items)

    return questions


def save(data, s3_bucket, filename):
    s3 = boto3.resource('s3')
    s3_object = s3.Object(s3_bucket, filename)
    s3_object.put(Body=data)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f'Usage: {sys.argv[0]} YYYY-mm-dd')
        sys.exit(1)

    date = sys.argv[1]
    page_size = os.getenv('SCRAPER_PAGE_SIZE', 200)
    s3_bucket = os.getenv('SCRAPER_S3_BUCKET', None)
    s3_object_prefix = os.getenv('SCRAPER_S3_OBJECT_PREFIX', 'answered_questions_')

    questions = get_questions(date=date, page_size=page_size)

    if s3_bucket:
        filename = f'{s3_object_prefix}{date}.json'
        save(json.dumps(questions), s3_bucket, filename)
    else:
        print(f'Questions for {date}: {questions}')
