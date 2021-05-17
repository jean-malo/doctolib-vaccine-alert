import configparser

from src.utils import read_config_value, to_list

config = configparser.ConfigParser()
config.read("config.ini")


SMTP_ENABLED = read_config_value(config, "smtp", "enabled", var_type=bool, fallback=False)
SLACK_ENABLED = read_config_value(config, "slack", "enabled", var_type=bool, fallback=False)
# Change to true to open a new tab when an appointment is found
BROWSER_ENABLED = read_config_value(config, "browser", "enabled", var_type=bool, fallback=True)

SLACK_WEBHOOK = read_config_value(config, "slack", "webhook")
SMTP_SERVER = read_config_value(config, "smtp", "server", fallback="smtp.gmail.com")
SMTP_LOGIN = read_config_value(config, "smtp", "login")
SMTP_PASSWORD = read_config_value(config, "smtp", "password")
SQL_LITE_DB_PATH = read_config_value(config, "core", "db_path", fallback="covid.db")
EMAIL_RECIPIENTS = to_list(read_config_value(config, "smtp", "recipients", fallback=""))
DOCTOLIB_SEARCH_URL = read_config_value(
    config,
    "core",
    "doctolib_search_url",
    fallback="https://www.doctolib.fr/vaccination-covid-19/paris-75001?page=1&ref_visit_motive_ids[]=6970&ref_visit_motive_ids[]=7005&force_max_limit=2",
)
RATE_LIMIT = read_config_value(
    config,
    "core",
    "rate_limit",
    fallback=60,
    var_type=int,
)
ALLOWED_ZIPCODES = to_list(
    read_config_value(config, "core", "allowed_zipcodes", fallback="")
)

PLURAL_INTRO = "Voici la liste des rendez-vous disponibles:"
SINGULAR_INTRO = "Voici le rendez-vous disponible:"
