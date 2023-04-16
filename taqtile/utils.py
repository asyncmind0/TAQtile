from libqtile.utils import send_notification as q_send_notification
from taqtile import QTILE_NOTIFICATION_ID


def send_notification(title, message):
    q_send_notification(
        title,
        str(message),
        timeout=1000,
        id_=QTILE_NOTIFICATION_ID,
    )
