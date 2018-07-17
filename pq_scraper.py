from urllib.parse import urlencode
import json
import sys

import requests



API_URL = "https://lda.data.parliament.uk/answeredquestions.json"


def _get_response_json(url):
    print(f"Requesting '{url}'...")

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


def save(data, filename):
    f = open(filename, mode="w")
    json.dump(data, f)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f'Usage: {sys.argv[0]} YYYY-mm-dd')
        sys.exit(1)

    date = sys.argv[1]
    questions = get_questions(date=date)

    filename = f"answered_questions_{date}.json"
    save(questions, filename=filename)
