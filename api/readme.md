The courbot API revolves around 2 endpoints.

* A `GET` endpoint that receives case query parameters and returns the court date.
* A `POST` endpoint that receives the court date and a phone number, and creates 2 text alerts: for 1 day before and 1 week before.

For a brigade to add themselves to courbot, they need to implement the first
`GET` API endpoint, and [file an
issue](https://github.com/codefortulsa/courtbot-python/issues/new) to add the
endpoint url to courtbot. If your API endpoint needs new case query
parameters in order to find the court date, please include them in the issue so
we can update the courtbot code to pass the required query parameters to your
endpoint.

# `GET` court date endpoint
This endpoint receives lookup data as url parameters and returns a JSON
response with an `arraignment_datetime` field containing the court date.

## Example url
***`https://courtbot-python.herokuapp.com/api/case?year=2019&county=Tulsa&case_num=1`***

## Example Response
```
{
    "arraignment_datetime": "2019-01-07T09:00:00", // required
    "case": { // optional
        "type": "CF",
        "year": "2019",
        "county": "Tulsa",
        "number": "1"
    }
}
```

# `POST` alerts endpoint
This endpoint receives the `arraignment_datetime` and a `phone_num` and creates
the text message alerts to be sent.

## Example URL
***`https://courtbot-python.herokuapp.com/api/reminders`***

## Example `POST` data
```
case_num=CF-2014-5203&phone_num=19182615259&arraignment_datetime=2019-09-17T08:00:00
```

# Expected Post Response
```
{
    "status": "201 Created",
    "week_before_datetime": "2018-12-31T09:00:00",
    "day_before_datetime": "2019-01-06T09:00:00"
}
```

