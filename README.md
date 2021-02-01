# pagerduty2md

```
○ → pip install -r requirements.txt
○ → python pager2md.py --help
Usage: pager2md.py [OPTIONS]

Options:
  --html           Print in html
  --teamid TEXT    [required]
  --start TEXT     The date format in 2021-01-28T03:30:21  [required]
  --duration TEXT  Duration for this query in hours  [required]
  --apikey TEXT    Pagerduty API key  [required]
  --help           Show this message and exit.
```
```
○ → python pager2md.py    --teamid {{TEAMID}} --apikey {{APIKEY}}  --start "2021-01-30 01:00:00" --duration  12
|Time(UTC)|Description|Status|Notes|
|---------|-----------|------|-----|
|2021-01-30T06:12:16Z|1 alert for Interface Status Down in FUK|resolved|Resolution Note: port harddown, disabled isis|
|2021-01-30T10:25:15Z|1 alert for Interface Status Down in ACK|resolved|Resolution Note: port harddown, disabled isis|
```
