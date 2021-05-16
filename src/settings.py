import os


def to_list(string_separated):
    if not string_separated:
        return []
    return string_separated.split(",")


SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
EMAIL_FROM = os.getenv("EMAIL_FROM")
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SQL_LITE_DB_PATH = os.getenv("SQL_LITE_DB_PATH")
MAX_PAGE_NO_RESULTS = 1
MAX_PAGINATION = 10
EMAIL_RECIPIENTS = to_list(os.getenv("EMAIL_RECIPIENTS"))
DOCTOLIB_SEARCH_URL = "https://www.doctolib.fr/vaccination-covid-19/france?page=1&ref_visit_motive_ids[]=6970&ref_visit_motive_ids[]=7005&force_max_limit=2"
PLURAL_INTRO = "Voici la liste des rendez-vous disponibles:"
SINGULAR_INTRO = "Voici le rendez-vous disponible:"
ZIPCODE_WHITE_LIST = to_list(os.getenv("ZIPCODE_WHITE_LIST"))
WAIT_BEFORE_RETRY = int(os.getenv("WAIT_BEFORE_RETRY"), 60) # time in seconds to wait before retrying to find appointment
