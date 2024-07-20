import logging

from libqtile import hook, qtile

from taqtile.widgets.togglebtn import ToggleButton
import websocket

logger = logging.getLogger(__name__)

try:
    import obsws_python as obs
except ImportError:
    logger.error("OBS python sdk not installed")

PRIVATE_GROUPS = ["webcon", "home", "slack", "mail", "crypto", "calendar"]


def initialize_obs_client(func):
    def wrapper(*args, **kwargs):
        try:
            if not getattr(qtile, "OBS_CLIENT", None):
                qtile.OBS_CLIENT = obs.ReqClient(
                    host="localhost", port=4444, timeout=3
                )
            qtile.OBS_CLIENT.get_version()
            return func(qtile.OBS_CLIENT, *args, **kwargs)
        except NameError:
            logger.error("obs integration failed")
        except Exception:
            #    websocket._exceptions.WebSocketConnectionClosedException,
            #    BrokenPipeError,
            # ):
            logger.error("obs webbsocket failed reconnecting")
            qtile.OBS_CLIENT = None
        except obs.error.OBSSDKRequestError as e:
            logger.error(f"obs request failed. {e}")
        except ConnectionRefusedError as e:
            logger.error(f"obs not running ?. {e}")

    return wrapper


@initialize_obs_client
def obs_switch_scene(obs_client, scenename):
    resp = obs_client.set_current_program_scene(scenename)
    logger.info(f"switch to {scenename} got response {resp}")
    return resp


@initialize_obs_client
def obs_pause_recording(obs_client):
    global prev_scene
    prev_scene = (
        obs_client.get_current_program_scene().current_program_scene_name
    )
    obs_switch_scene("face")
    qtile.spawn("dunstctl set-paused true")


@initialize_obs_client
def obs_resume_recording(obs_client):
    global prev_scene
    obs_switch_scene(prev_scene)
    qtile.spawn("dunstctl set-paused false")


@initialize_obs_client
def obs_get_recording_state(obs_client):
    return obs_client.get_record_status().output_active


@initialize_obs_client
def obs_start_record(obs_client):
    resp = obs_client.start_record()
    logger.info(f"pause got response {resp}")
    return resp


@initialize_obs_client
def obs_stop_record(obs_client):
    resp = obs_client.start_record()
    logger.info(f"pause got response {resp}")
    return resp


@hook.subscribe.setgroup
def change_group_obs_hook():
    scene = {1: "output", 0: "main", 2: "log"}[qtile.current_screen.index]
    if qtile.current_group.name == "2":
        scene = "face"
    if qtile.current_group.name in PRIVATE_GROUPS:
        scene = "face"
        # obs_pause_recording()
    # else:
    #    obs_resume_recording()

    obs_switch_scene(scene)


class OBSStatusWidget(ToggleButton):
    def execute(self):
        if self.active:
            logger.info("Starting recording %s" % obs_start_record())
        else:
            logger.info("Stoped recording %s" % obs_stop_record())

    def check_state(self):
        try:
            self.active = obs_get_recording_state()
        except Exception:
            logger.error("checking obs state")
            self.active = False
        return super().check_state()
