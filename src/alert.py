import locale
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dateparser
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from . import settings

locale.setlocale(locale.LC_TIME, "fr_FR")

new_line = "\n"



def get_slack_message(vaccines):
    message = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":alert: Des rendez-vous pour se faire vacciner sont disponibles :alert:",
            },
        },
        {"type": "divider"},
    ]
    for vaccine in vaccines:
        message.extend(
            [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": vaccine["name"],
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Adresse* _{vaccine['address']}_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Date{'s' if len(vaccine['starts']) > 1 else ''}*\n{new_line.join(format_date(vaccine['starts']))}",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Prendre un rendez vous",
                                "emoji": True,
                            },
                            "value": "click_me_123",
                            "url": vaccine["url"],
                        }
                    ],
                },
                {"type": "divider"},
            ]
        )
    return message


def send_slack_alert(vaccines):
    client = WebClient(token=settings.SLACK_TOKEN)
    channel_id = settings.SLACK_CHANNEL_ID

    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            blocks=get_slack_message(vaccines),
            text=":alert: Des rendez-vous pour se faire vacciner sont disponibles :alert:",
        )

    except SlackApiError as e:
        print(f"Error posting message: {e}")


def format_date(dates, language="SLACK"):
    if language == "SLACK":
        code = "`"
        accentuate = "*"
        code_end = "`"
        code_block = "```"
        accentuate_end = "*"
        new_line = "\n"
        prefix, suffix = "", ""
    else:
        code = "<b>"
        code_end = "</b>"
        code_block = ""
        accentuate = "<b>"
        accentuate_end = "</b>"
        new_line = "<br>"
        prefix, suffix = "<li>", "</li>"
    dates_msg = []
    for availability in dates:
        day = dateparser.parse(availability["date"])
        hours = ", ".join(
            [
                dateparser.parse(date["start_date"]).strftime("%Hh%M")
                for date in availability["slots"]
            ]
        )
        dates_msg.append(
            day.strftime(
                f"{prefix}{code}%A %d %B %Y{code_end}{new_line}{accentuate}Créneau{'x' if len(availability['slots']) > 1 else ''} disponible{'s' if len(availability['slots']) > 1 else ''}:{accentuate_end} {code_block}{hours}{code_block}{suffix}"
            )
        )
    return dates_msg


def get_text_mail(vaccines):
    return "\n\n".join(
        [
            f"Centre: {vaccine['name']}\nDate{'s' if len(vaccine['starts']) > 1 else ''}\n\n{new_line.join(format_date(vaccine['starts']))} \n"
            f"Lien pour reserver {vaccine['url']}"
            for vaccine in vaccines
        ]
    )


def already_sent(profile_id, sent_at):
    conn = sqlite3.connect("covid.db")
    cursor = conn.execute(
        "SELECT count(*) from SENT where profile_id=? AND sent_at=?",
        (profile_id, sent_at),
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] > 0


def mark_as_sent(vaccines):
    ids = [
        (vac["""profile_id"""], slot["start_date"])
        for vac in vaccines
        for start in vac["starts"]
        for slot in start["slots"]
    ]
    conn = sqlite3.connect("covid.db")
    conn.executemany("INSERT INTO SENT(profile_id, sent_at) VALUES (?, ?)", ids)
    conn.commit()
    conn.close()


def get_html_mail(vaccines, plural=True):
    list = (
        "<ul>\n"
        + "\n".join(
            [
                "<li>".rjust(8) + f"<b>Centre: </b><br>{vaccine['name']}<br>"
                f"<b>Date{'s' if len(vaccine['starts']) > 1 else ''}: </b><br><ul>{' '.join(format_date(vaccine['starts'], language='HTML'))}</ul>"
                f"<b>Adresse: </b> {vaccine['address']}"
                f"<br><b><a href=\"{vaccine['url']}\">Lien pour reserver</a></b><br>"
                + "</li>"
                for vaccine in vaccines
            ]
        )
        + "\n</ul>"
    )
    return f"""<html>
          <head></head>
          <body>
            <p>Bonjour!<br>{settings.PLURAL_INTRO if plural else settings.SINGULAR_INTRO}</p>
            {list}
          </body>
        </html>
"""


def send_alert(vaccines):
    for vac in vaccines:
        for start in vac["starts"]:
            start["slots"] = [
                i
                for i in start["slots"]
                if not already_sent(vac["profile_id"], i["start_date"])
            ]
        vac["starts"] = [i for i in vac["starts"] if i["slots"]]
    vaccines = [v for v in vaccines if v["starts"]]
    if not vaccines:
        print("all sent already")
    else:
        send_mail_alert(vaccines)
        send_slack_alert(vaccines)
        mark_as_sent(vaccines)


def send_mail_alert(vaccines):
    for email in settings.EMAIL_RECIPIENTS:
            msg = MIMEMultipart("alternative")
            msg_text = (
                MIMEText(f"Bonjour! \n {settings.PLURAL_INTRO}\n\n{get_text_mail(vaccines)}")
                if len(vaccines) > 1
                else MIMEText(
                    f"Bonjour! \n {settings.SINGULAR_INTRO} \n {get_text_mail(vaccines)}"
                )
            )
            msg_html = (
                MIMEText(
                    f"{get_html_mail(vaccines)}",
                    "html",
                )
                if len(vaccines) > 1
                else MIMEText(
                    f"{get_html_mail(vaccines, plural=False)}",
                    "html",
                )
            )
            msg["Subject"] = (
                f"🚨 Des rendez-vous pour se faire vacciner sont disponibles 🚨 "
                if len(vaccines) > 1
                else f"🚨 Un rendez-vous pour se faire vacciner est disponible 🚨 "
            )
            msg.attach(msg_text)
            msg.attach(msg_html)
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = email
            server_ssl = smtplib.SMTP_SSL(settings.SMTP_SERVER, 465)
            server_ssl.ehlo()  # optional, called by login()
            server_ssl.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
            server_ssl.sendmail(msg["From"], msg["To"], msg.as_string())
