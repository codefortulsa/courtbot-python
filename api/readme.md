# Example Get Request
***`https://courtbot-python.herokuapp.com/api/case?year=2019&county=Tulsa&case_num=1`***

# Expected Get Response
```
{
    "case": {
        "type": "CF",
        "year": "2019",
        "county": "Tulsa",
        "number": "1"
    },
    "arraignment_datetime": "2019-01-07T09:00:00"
}
```

# Example Post Request
***`https://courtbot-python.herokuapp.com/api/reminders`***
form-data = {
    "arraignment_datetime": "2019-01-11T09:00:00",
    "case_num": 1,
    "phone_num": "+1-918-555-5555"
}

# Expected Post Response
```
{
    "status": "201 Created"
}
```

