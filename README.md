# doctolib-vaccine-alert
Bot that scrapes Doctolib to find available vaccination time slots

Have a look at [config.ini](./config.ini) for the available settings.

You should modify the config or add the relevant env vars before running the script.

🚧 This is a WIP, I will improve it and add more features when I have more time, feel free to open PRs if you have features that you want to add.  

While it was designed for vaccines if you modify the query by changing `core.doctolib_search_url` in `config.ini` you could fetch appointments for any city & any subject. 

# Getting started

## Configuration

You can configure most settings in the file [config.ini](./config.ini). If you do not wish to edit the file directly you configure it via environment variables.
Example: `SMTP__PASSWORD` will override what is set in the config `smtp.password`


## Requirements
When the script first runs if the table `SENT` does not exist in the sqlite db that you specified (or the default `msg_sents.db`) it will be created.
You can change the path of the db in the config file using the entry `core.db_path`

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

## Running locally

```python
poetry install && poetry shell && python -m src.main
```

## Running with docker

```python
docker build . -t doctolib-vaccine-finder && docker run --rm --env-file=.env doctolib-vaccine-finder
```
