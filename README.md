# pq_scraper
Parliamentary Questions (PQ) scraper

### API
The data is scraped from https://lda.data.parliament.uk/answeredquestions.json

### Usage
Invoke the scraper with the following command will scrape the answered questions
for the 31st March 2018:

```bash
$ python3 pq_scraper 2018-03-31
```

### Environment variables

| **Name** | **Description** | **Default** |
| -------- | --------------- | ----------- |
| `SCRAPER_PAGE_SIZE` | How many questions to request at each API call | `200` |
| `SCRAPER_S3_BUCKET` | S3 bucket where to write the questions. | `""` (questions are not written to S3 unless this is provided) |
| `SCRAPER_S3_OBJECT_PREFIX` | Prefix of the "file" (S3 object) where to write the questions. This will include the path if any, e.g. `"/path/to/raw/answered_questions_"` will result in the questions for the date `2018-06-30` being written to `/path/to/raw/answered_questions_2018-06-30.json` | `"answered_questions_"` |

**NOTE** If `SCRAPER_S3_BUCKET` is not set the questions will be simply
be printed to stdout (standard output).
