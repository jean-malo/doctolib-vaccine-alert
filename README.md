# doctolib-vaccine-alert
Bot that scrapes Doctolib to find available vaccination time slots

Have a look at [settings.py](./src/settings.py) and [.env.example](.env.example) for the available settings.

You should add the relevant env vars before running the script.

🚧 This was built in a few hours so excuse the code quality, I will improve it and add more features when I have more time.  

While it was designed for vaccines if you modify the query by changing `core.doctolib_search_url` in `config.ini` you could fetch appointments for any city & any subject. 

# Getting started

## Requirements

You will need an sqlite db with the following table. You can change the path in the config file using the entry var `core.db_path`

It is used to keep tack of which appointments have been sent. If the table `SENT` does not exist it will be created when you first launch the script.

```sql
create table SENT
(
    profile_id INT not null,
    sent_at    CHAR(140)
);

create index idx_profile_sent
    on SENT (profile_id, sent_at);
```

## Running locally

```python
poetry install && poetry shell && python -m src.main
```

## Run with docker

```python
docker build . -t doctolib-vaccine-finder && docker run --rm --env-file=.env doctolib-vaccine-finder
```

## Configuration

You can configure most settings in the file [config.ini](./config.ini). If you do not wish to edit the file directly you configure it via environment variables.
Example: `SMTP__PASSWORD` will override what is set in the config `smtp.password`

