from taqtile.dmenu import dmenu_kubectl, switch_pulse
from mock import Mock


def test_dmenu_kubectl():
    return dmenu_kubectl(Mock())


def test_switch_pulse():
    return switch_pulse(Mock())
