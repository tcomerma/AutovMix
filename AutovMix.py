#####################################################################
#  AutovMix.py
#
#  Remota un vMix via API per demo de les possibilitats que té
#
#####################################################################

# Imports
import argparse
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
import sched
import time
import datetime
import untangle
import logging


class vMix:
    def __init__(self, config):
        self.url = config["parameters"]["url"]
        self.username = config["parameters"]["username"]
        self.password = config["parameters"]["password"]
        self.state = ""

    def request(self, cmd):

        if cmd == "":
            url = self.url + "/api/"
        else:
            url = self.url + "/api/?function=" + cmd
        log.debug(f"Invoking {url}")
        try:
            response = requests.get(url,
                                    auth=HTTPBasicAuth(self.username, self.password), timeout=10)
            if response.status_code != 200:
                log.error(
                    f"Error retornat per vMix Codi: {response.status_code} Text: {response.text}")
        except:
            log.error("problema contactant amb vMIX")
        return response

    def update_state(self):
        r = self.request("")
        self.state = untangle.parse(r.text)
        log.debug(r.text)

    def version(self):
        self.update_state()
        return (self.state.vmix.version.cdata)


def act_loadProfile(config, v):
    log.info("Executant act_loadProfile @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("OpenPreset&value=" + config["parameters"]["preset"])
    v.request("CutDirect&Input=3")
    v.request("AddInput&Value=Video|"+config["parameters"]["loop"])
    v.request("AddInput&Value=Image|"+config["parameters"]["logo"])
    #time.sleep (10)
    v.request("SetZoom&Value=0.2&Input=5")
    v.request("SetPanX&Value=0.8&Input=5")
    v.request("SetPanY&Value=0.8&Input=5")
    v.request("MoveInput&Value=1&Input=4")
    v.request("MoveInput&Value=2&Input=5")
    v.request("OverlayInputAllOff")
    v.request("SetText&Input=3&Value=" + config["parameters"]["titol"])
    v.request("NDISelectSourceByName&Input=4&Value=" +
              config["parameters"]["font"])


def act_caratula(config, v):
    log.info("Executant act_caratula @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("CutDirect&Input=1")
    v.request("OverlayInput2In&Input=3")
    v.request("OverlayInput1In&Input=2")


def act_iniciaGravacio(config, v):
    log.info("Executant act_iniciaGravacio @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StartRecording")


def act_finalitzaGravacio(config, v):
    log.info("Executant act_finalitzaGravacio @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StopRecording")


def act_iniciaStreaming(config, v):
    log.info("Executant act_iniciaStreaming @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StartStreaming")


def act_finalitzaStreaming(config, v):
    log.info("Executant act_finalitzaStreaming @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StopStreaming")


def act_programa(config, v):
    log.info("Executant act_programa @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("OverlayInput2Out&Input=3")
    v.request("CutDirect&Input=4")
    v.request("OverlayInput1In&Input=2")


def act_off(config, v):
    log.info("act_off @" + datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("CutDirect&Input=5")
    v.request("OverlayInputAllOff")
    # v.request("StopRecording")


def connect(config, v):
    log.info("Connecting")
    log.info("Connected to version " + v.version())


def disconnect(config):
    log.info("disconnecting")


def schedule(config, v):
    log.info("scheduling")
    s = sched.scheduler(time.time, time.sleep)
    # Planificar arrancada
    if config["start_time"] == "now":
        t = datetime.datetime.now()
    else:
        t = datetime.datetime.strptime(
            config["start_time"], "%d/%m/%Y %H:%M:%S")
    t2 = t + datetime.timedelta(0, 2)
    log.info(f"act_loadProfile scheduled @ {t2}")
    s.enterabs(t2.timestamp(), 1, act_loadProfile, argument=(config, v,))
    for k in config["events"]:
        delay = config["events"][k]["delay"]
        action = config["events"][k]["action"]
        t = t + datetime.timedelta(0, int(delay))
        if action == "caratula":
            s.enterabs(t.timestamp(), 1, act_caratula, argument=(config, v,))
            log.info(f"act_caratula scheduled @ {t}")
        elif action == "programa":
            s.enterabs(t.timestamp(), 1, act_programa, argument=(config, v,))
            log.info(f"act_programa scheduled @ {t}")
        elif action == "iniciaGravacio":
            s.enterabs(t.timestamp(), 1, act_iniciaGravacio,
                       argument=(config, v,))
            log.info(f"act_iniciaGravacio scheduled @ {t}")
        elif action == "finalitzaGravacio":
            s.enterabs(t.timestamp(), 1, act_finalitzaGravacio,
                       argument=(config, v,))
            log.info(f"act_finalitzaGravacio scheduled @ {t}")
        elif action == "iniciaStreaming":
            s.enterabs(t.timestamp(), 1, act_iniciaStreaming,
                       argument=(config, v,))
            log.info(f"act_iniciaStreaming scheduled @ {t}")
        elif action == "finalitzaStreaming":
            s.enterabs(t.timestamp(), 1, act_finalitzaStreaming,
                       argument=(config, v,))
            log.info(f"act_finalitzaStreaming scheduled @ {t}")
        elif action == "off":
            s.enterabs(t.timestamp(), 1, act_off, argument=(config, v,))
            log.info(f"act_off scheduled @ {t}")
    log.info("Running...")
    s.run()


def main():

    log.info("Iniciant")
    # Parse command line

    parser = argparse.ArgumentParser(description='Process line parameters.')
    parser.add_argument('--file', '-f', dest='file',
                        help='file config')
    parser.add_argument('--debug', '-d', dest='debug',
                        action='store_true', help='print debug info')
    args = parser.parse_args()

    if (args.file is None):
        log.error("No file indicated")
        exit(1)

    if (args.debug is True):
        log.setLevel(logging.DEBUG)

    # Open config file
    try:
        with open(args.file, 'r') as file:
            config = json.loads(file.read())
    except Exception as e:
        log.error(f"Problems opening file {args.file}")
        log.error(e)
        exit(3)

    v = vMix(config)
    connect(config, v)
    schedule(config, v)
    disconnect(config)


if __name__ == "__main__":
    log = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    log.addHandler(ch)
    log.setLevel(logging.INFO)

    main()
    exit(0)
