import logging

import pulsectl

from taqtile.widgets.togglebtn import ToggleButton
from pprint import pformat


logger = logging.getLogger(__name__)


class VoiceInputStatusWidget(ToggleButton):
    def _check_state(self):
        found = False
        with pulsectl.Pulse("voice-input-status-widget") as pulse:
            # Get a list of all source outputs (recording streams)
            source_outputs = pulse.source_output_list()
            sources = pulse.source_list()

            # Create a dictionary of sources with their index as the key
            sources_dict = {source.index: source for source in sources}

            # Print information about each source output with an active parent source
            for source_output in source_outputs:
                parent_source = sources_dict.get(source_output.source)

                if parent_source and parent_source.state == "running":
                    app_name = source_output.proplist.get(
                        "application.name", "Unknown"
                    )
                    app_id = source_output.proplist.get(
                        "application.id", "Unknown"
                    )
                    if app_id == "org.PulseAudio.pavucontrol":
                        continue
                    return True

                    # print(f"App name: {app_name}")
                    # print(f"Source output index: {source_output.index}")
                    # print(f"Source index: {source_output.source}")
                    # print(f"Volume: {source_output.volume}")
                    # print(f"Mute: {source_output.mute}")
                    # print(f"Sample spec: {source_output.sample_spec}")
                    # print(f"Proplist: {source_output.proplist}")
                    # print("=" * 40)
        return found

    def check_state(self):
        self.active = self._check_state()
        return super().check_state()
