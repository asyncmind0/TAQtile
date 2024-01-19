from libqtile.utils import send_notification as q_send_notification
from taqtile import QTILE_NOTIFICATION_ID
import asyncio
from libqtile.log_utils import logger
from random import randint
from typing import Any

try:
    from dbus_next import AuthError, Message, Variant
    from dbus_next.aio import MessageBus
    from dbus_next.constants import BusType, MessageType

    has_dbus = True
except ImportError:
    has_dbus = False


def send_notification0(title, message):
    q_send_notification(
        title,
        str(message),
        timeout=1000,
        id_=QTILE_NOTIFICATION_ID,
    )


def send_notification(
    title: str,
    message: str,
    urgent: bool = False,
    timeout: int = -1,
    id_: int | None = QTILE_NOTIFICATION_ID,
    value: int | None = None,
) -> int:
    """
    Send a notification.

    The id_ argument, if passed, requests the notification server to replace a visible
    notification with the same ID. An ID is returned for each call; this would then be
    passed when calling this function again to replace that notification. See:
    https://developer.gnome.org/notification-spec/
    """
    if not has_dbus:
        logger.warning(
            "dbus-next is not installed. Unable to send notifications."
        )
        return -1

    id_ = randint(10, 1000) if id_ is None else id_
    urgency = 2 if urgent else 1

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        logger.warning("Eventloop has not started. Cannot send notification.")
    else:
        loop.create_task(_notify(title, message, urgency, timeout, id_, value))

    return id_


async def _notify(
    title: str, message: str, urgency: int, timeout: int, id_: int, value: int
) -> None:
    notification = [
        "qtile",  # Application name
        id_,  # id
        "",  # icon
        title,  # summary
        message,  # body
        [],  # actions
        {
            "urgency": Variant("y", urgency),
            "value": Variant("u", value),
        },  # hints
        timeout,
    ]  # timeout

    bus, msg = await _send_dbus_message(
        True,
        MessageType.METHOD_CALL,
        "org.freedesktop.Notifications",
        "org.freedesktop.Notifications",
        "/org/freedesktop/Notifications",
        "Notify",
        "susssasa{sv}i",
        notification,
    )

    if msg and msg.message_type == MessageType.ERROR:
        logger.warning(
            "Unable to send notification. Is a notification server running?"
        )

    # a new bus connection is made each time a notification is sent so
    # we disconnect when the notification is done
    if bus:
        bus.disconnect()


async def _send_dbus_message(
    session_bus: bool,
    message_type: MessageType,
    destination: str | None,
    interface: str | None,
    path: str | None,
    member: str | None,
    signature: str,
    body: Any,
    negotiate_unix_fd: bool = False,
) -> tuple[MessageBus | None, Message | None]:
    """
    Private method to send messages to dbus via dbus_next.

    Returns a tuple of the bus object and message response.
    """
    if session_bus:
        bus_type = BusType.SESSION
    else:
        bus_type = BusType.SYSTEM

    if isinstance(body, str):
        body = [body]

    try:
        bus = await MessageBus(
            bus_type=bus_type, negotiate_unix_fd=negotiate_unix_fd
        ).connect()
    except (AuthError, Exception):
        logger.warning("Unable to connect to dbus.")
        return None, None

    # Ignore types here: dbus-next has default values of `None` for certain
    # parameters but the signature is `str` so passing `None` results in an
    # error in mypy.
    msg = await bus.call(
        Message(
            message_type=message_type,
            destination=destination,
            interface=interface,
            path=path,
            member=member,
            signature=signature,
            body=body,
        )
    )

    return bus, msg
