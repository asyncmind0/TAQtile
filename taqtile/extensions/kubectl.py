from libqtile.extension.dmenu import Dmenu
from plumbum.cmd import kubectl
import json


class KubeCtl(Dmenu):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    dmenu_prompt = "Kubectl"

    def run(self, items=None):
        clusters = kubectl("config", "get-clusters").split()
        cluster = super().run(clusters)
        pods = json.loads(
            kubectl("--context", cluster, "get", "po", "-o", "json")
        )
        return super().run(pods)
