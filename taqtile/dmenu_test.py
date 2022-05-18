from taqtile.dmenu import dmenu_kubectl
from mock import Mock


def test_dmenu_kubectl():
    return dmenu_kubectl(Mock())
