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
from flask import Flask, render_template, redirect, jsonify, request, current_app
from flask_apscheduler import APScheduler

class Config:
    SCHEDULER_API_ENABLED = True


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
        app.logger.debug(f"Invoking {url}")
        try:
            print (url)
            response = requests.get(url,
                                    auth=HTTPBasicAuth(self.username, self.password), timeout=10)
            if response.status_code != 200:
                print (f"Error retornat per vMix Codi: {response.status_code} Text: {response.text}")
                app.logger.error(
                    f"Error retornat per vMix Codi: {response.status_code} Text: {response.text}")
        except:
            app.logger.error("problema contactant amb vMIX")
        return response

    def update_state(self):
        r = self.request("")
        self.state = untangle.parse(r.text)
        app.logger.debug(r.text)

    def version(self):
        self.update_state()
        return (self.state.vmix.version.cdata)


def act_loadProfile(config, v):
    app.logger.info("Executant act_loadProfile @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("OpenPreset&value=" + config["parameters"]["preset"])
    v.request("CutDirect&Input=3")
    v.request("AddInput&Value=Video|"+config["parameters"]["loop"])
    v.request("AddInput&Value=Image|"+config["parameters"]["logo"])
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
    app.logger.info("Executant act_caratula @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("CutDirect&Input=1")
    v.request("OverlayInput2In&Input=3")
    v.request("OverlayInput1In&Input=2")


def act_iniciaGravacio(config, v):
    app.logger.info("Executant act_iniciaGravacio @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StartRecording")


def act_finalitzaGravacio(config, v):
    app.logger.info("Executant act_finalitzaGravacio @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StopRecording")


def act_iniciaStreaming(config, v):
    app.logger.info("Executant act_iniciaStreaming @" +
            datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StartStreaming")


def act_finalitzaStreaming(config, v):
    app.logger.info("Executant act_finalitzaStreaming @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("StopStreaming")


def act_programa(config, v):
    app.logger.info("Executant act_programa @" +
             datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("OverlayInput2Out&Input=3")
    v.request("CutDirect&Input=4")
    v.request("OverlayInput1In&Input=2")


def act_off(config, v):
    app.logger.info("act_off @" + datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
    v.request("CutDirect&Input=5")
    v.request("OverlayInputAllOff")
    # v.request("StopRecording")


def schedule(scheduler,config, v):
    app.logger.info("scheduling")
    scheduler.remove_all_jobs()
    # Planificar arrancada
    if config["start_time"] == "now":
        t = datetime.datetime.now()
    else:
        t = datetime.datetime.strptime(
            config["start_time"], "%d/%m/%Y %H:%M:%S")
    t2 = t + datetime.timedelta(0, 2)
    app.logger.info(f"act_loadProfile scheduled @ {t2}")
    scheduler.add_job(func=act_loadProfile, trigger='date', id='loadProfile', run_date=t2, args=[config, v])
    for k in config["events"]:
        delay = config["events"][k]["delay"]
        action = config["events"][k]["action"]
        t = t + datetime.timedelta(0, int(delay))
        if action == "caratula":
            scheduler.add_job(func=act_caratula, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_caratula scheduled @ {t}")
        elif action == "programa":
            scheduler.add_job(func=act_programa, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_programa scheduled @ {t}")
        elif action == "iniciaGravacio":
            scheduler.add_job(func=act_iniciaGravacio, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_iniciaGravacio scheduled @ {t}")
        elif action == "finalitzaGravacio":
            scheduler.add_job(func=act_finalitzaGravacio, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_finalitzaGravacio scheduled @ {t}")
        elif action == "iniciaStreaming":
            scheduler.add_job(func=act_iniciaStreaming, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_iniciaStreaming scheduled @ {t}")
        elif action == "finalitzaStreaming":
            scheduler.add_job(func=act_finalitzaStreaming, trigger='date', id=k, run_date=t, args=[config, v])
            app.logger.info(f"act_finalitzaStreaming scheduled @ {t}")
        elif action == "off":
            scheduler.add_job(func=act_off, trigger='date', id=k, run_date=t, args=[config, v])
    app.logger.info("Running...")

def schedule2dict():
    s = []

    for j in scheduler.get_jobs():
        sj = {}
        sj ['name'] = j.id
        sj ['date'] = j.next_run_time
        sj ['action'] = j.func.__name__
        s.append(sj)
    return (s)

# create app
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
vmix = None
config = None

@app.route('/')
def index():
    global config
    global scheduler
    if config is None:
        c = "No carregada"
    else:
        c = config
    return render_template(
        'index.html',
        config=json.dumps(c, indent=4), jobs=schedule2dict())

@app.route('/config', methods=['GET', 'POST'])
def read_config():
    global vmix
    global config
    global scheduler
    if request.method == 'POST':
        config_text = request.form['config']
        try:
            config = json.loads(config_text)
        except Exception as err:
            return render_template('error.html', error=f"Parsejant config:{err}")
        app.logger.info ("Configuracio parsejada")
        app.logger.info (config)
        vmix = vMix(config)
        schedule (scheduler, config, vmix)
        return redirect("/")
    else:
        return render_template('config.html')

@app.route('/accio/aPrograma')
def aPrograma():
    global vmix
    global config
    app.logger.info ("Anem a Programa")
    act_programa (config, vmix)
    return ("A Programa hem anat")

@app.route('/accio/aNegre')
def aNegre():
    global vmix
    global config
    app.logger.info ("Anem a Negre")
    act_off (config, vmix)
    return ("A Negre hem anat")

@app.route('/accio/aCareta')
def aCareta():
    global vmix
    global config
    app.logger.info ("Anem a Careta")
    act_caratula (config, vmix)
    return ("A Careta hem anat")

@app.route('/accio/iniciaStreaming')
def iniciaStreaming():
    global vmix
    global config
    app.logger.info ("Iniciem Streaming")
    act_iniciaStreaming (config, vmix)
    return ("Streaming Iniciat")

@app.route('/accio/finalitzaStreaming')
def finalitzaStreaming():
    global vmix
    global config
    app.logger.info ("Finalitzem Streaming")
    act_finalitzaStreaming (config, vmix)
    return ("Streaming Finalitzat")

@app.route('/accio/iniciaGravacio')
def iniciaGravacio():
    global vmix
    global config
    app.logger.info ("Iniciem Gravacio")
    act_iniciaGravacio (config, vmix)
    return ("Gravacio Iniciat")

@app.route('/accio/finalitzaGravacio')
def finalitzaGravacio():
    global vmix
    global config
    app.logger.info ("Finalitzem Gravacio")
    act_finalitzaGravacio (config, vmix)
    return ("Gravacio Finalitzat")

if __name__ == '__main__':
    app.run()