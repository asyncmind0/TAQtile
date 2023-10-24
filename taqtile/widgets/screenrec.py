from taqtile.widgets.togglebtn import ToggleButton
from os.path import expanduser
import subprocess
from datetime import datetime


class ScreenRecord(ToggleButton):
    process = None
    active = False

    def execute(self):
        if self.active:
            if self.process is None:
                # Start the process
                # wid = subprocess.check_output(["xprop"]).decode().strip()

                self.process = subprocess.Popen(
                    [
                        "recordmydesktop",
                        f"--windowid={self.qtile.current_window.window.wid}",
                        "--on-the-fly-encoding",
                        "--overwrite",
                        "--device",
                        "pulse",
                        "-o",
                        expanduser(
                            f"~/screenrecordings/qtilerec_{datetime.utcnow().strftime('%Y%m%d%H%M')}.ogv"
                        ),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.text = "RMD - Recording"
        elif self.process:
            # Stop the process
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.text = "RMD"
