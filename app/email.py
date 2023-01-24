from threading import Thread
from flask_mail import Message
from flask import current_app, render_template

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        f"{app.config['DIBS_MAIL_SUBJECT_PREFIX']} {subject}",
        sender=app.config["DIBS_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(f"{template}.txt", **kwargs)
    msg.html = render_template(f"{template}.html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
