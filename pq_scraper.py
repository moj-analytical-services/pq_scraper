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
    """
    Gets the answered PQs from the parliament.uk public API

    Args:
        date (str): Date for which to get the questions. Date must be in
            ISO 8601 format (`YYYY-mm-dd`)
        page_size (int, optional, default: 200): Number of questions to request
            at each API call

    Returns:
        list: List of all answered PQs for the specified date sorted by ID (uin).
            The list items are in the same format as returned by the API (
            `["result"]["items"] elements from responses)

    Raises:
        Exception: Raised when one of the request response status is not `200 OK`
    """

    questions = []
    for page_items in _result_pages(date=date, page_size=page_size):
        questions.extend(page_items)

    return questions


def save(data, s3_bucket, filename):
    """
    Saves the data to S3

    Args:
        data: data to save
        s3_bucket (str): S3 bucket where to save the data
        filename (str): S3 key where to save the data

    Examples:
        >>> import json
        >>> data = {'foo': 'bar'}
        >>> save(json.dumps(data), 'my_bucket', 'my_file.json')
    """

    s3 = boto3.resource("s3")
    s3_object = s3.Object(s3_bucket, filename)
    s3_object.put(Body=data)


def main():
    """
    Scrapes the answered Parliamentary Questions (PQ) for the date.

    It prints them to stdout (standard output) if the `SCRAPER_S3_BUCKET`
    environment variable is not set.

    It saves them to the given S3 bucket if the `SCRAPER_S3_BUCKET` environment
    variable is set. The filename can be configured by setting the
    `SCRAPER_S3_OBJECT_PREFIX` environment variable.

    Usage:
        $ python3 pq_scraper.py DATE

        *NOTE*: DATE must be a date in ISO 8601 format (`YYYY-mm-dd`)

    Examples:
        $ python3 pq_scraper.py 2017-07-30
        (print to stdout the answered PQs asked on 30th July 2017)

        $ SCRAPER_S3_BUCKET="my_bucket" python3 pq_scraper.py 2017-07-30
        (saves the answered PQs asked on 30th July 2017 to the `my_bucket` S3
        bucket, in the `answered_questions_2017-07-30.json` object)

        $ SCRAPER_S3_BUCKET="my_bucket" SCRAPER_S3_OBJECT_PREFIX="pqs_" python3 pq_scraper.py 2017-07-30
        (saves the answered PQs asked on 30th July 2017 to the `my_bucket` S3
        bucket, in the `pqs_2017-07-30.json` object)
    """

    if len(sys.argv) == 1:
        print(f"Usage: {sys.argv[0]} YYYY-mm-dd")
        sys.exit(1)

    date = sys.argv[1]
    page_size = os.getenv("SCRAPER_PAGE_SIZE", 200)
    s3_bucket = os.getenv("SCRAPER_S3_BUCKET", None)
    s3_object_prefix = os.getenv("SCRAPER_S3_OBJECT_PREFIX", "answered_questions_")

    questions = get_questions(date=date, page_size=page_size)

    if s3_bucket:
        filename = f"{s3_object_prefix}{date}.json"
        save(json.dumps(questions), s3_bucket, filename)
    else:
        print(f"Questions for {date}: {questions}")


if __name__ == "__main__":
    main()
