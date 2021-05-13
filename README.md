# doctolib-vaccine-alert
Bot that scrapes Doctolib to find available vaccination time slots

Have a look at [settings.py](./src/settings.py) and [.env.example](.env.example) for the available settings.

You should add the relevant env vars before running the script.

🚧 This was built in a few hours so excuse the code quality, I will improve it and add more features when I have more time.  

While it was designed for vaccines if you modify the query by changing `DOCTOLIB_SEARCH_URL` in `settings.py` you could fetch appointments for any city & any subject. 

# Getting started

## Requirements

You will need an sqlite db with the following table. You can change the path in the settings file using the env var `SQL_LITE_DB_PATH`


It is used to keep tack of which appointments have been sent.

```sql
create table SENT
(
    profile_id INT not null,
    sent_at    CHAR(140)
);

create index idx_profile_sent
    on SENT (profile_id, sent_at);
```

## Run locally

```python
poetry install && poetry shell && python -m src.main
```

## Run with docker

```python
docker build . -t doctolib-vaccine-finder && docker run --rm  --env-file=.env doctolib-vaccine-finder
```
