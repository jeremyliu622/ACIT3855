import logging.config
import connexion
import yaml
import json
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import datetime
import os
import requests
from flask_cors import CORS, cross_origin

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config["data_store"]["filename"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")


def get_stats():
    """get the stats on readings"""
    logger.info("-"*15 + "Receive Get Current Statistics request" + "-"*15)

    if not os.path.isfile(data_file):
        error_message = "Statistics do not exist"
        logger.error(error_message)
        logger.info("-"*15 + "End of Get Current Statistics request" + "-"*15)

        return error_message, 404

    with open(data_file, "r") as json_file:
        current_stats = json.load(json_file)
    logger.debug(json.dumps(current_stats))
    logger.info("-"*15 + "End of Get Current Statistics request" + "-"*15)

    return current_stats, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("-"*15 + "Start Periodic Processing" + "-"*15)
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if os.path.isfile(data_file):
        with open(data_file, "r") as json_file:
            current_stats = json.load(json_file)
            last_updated = current_stats["last_updated"]
    else:
        current_stats = {
            "num_bi_readings": 0,
            "max_bi_quantity_readings": 0,
            "num_ph_readings": 0,
            "max_ph_quantity_readings": 0
        }
        last_updated = current_time

    # current_time = "2021-10-05T08:54:02Z"
    payload = {
        "start_timestamp": last_updated,
        "end_timestamp": current_time
               }

    r_bi = requests.get(app_config["get_book_inventory"], params=payload)
    if r_bi.status_code != 200:
        logger.error(r_bi.reason)
    else:
        bi_list = r_bi.json()
        logger.info("Query for getting Book Inventory after %s returns %d results" % (last_updated, len(bi_list)))
        current_stats["num_bi_readings"] += len(bi_list)
        for book_inventory in bi_list:
            if book_inventory["quantity"] > current_stats["max_bi_quantity_readings"]:
                current_stats["max_bi_quantity_readings"] = book_inventory["quantity"]

    r_ph = requests.get(app_config["get_purchase_history"], params=payload)
    if r_ph.status_code != 200:
        logger.error(r_ph.reason)
    else:
        ph_list = r_ph.json()
        logger.info("Query for getting Purchase History after %s returns %d results" % (last_updated, len(ph_list)))
        current_stats["num_ph_readings"] += len(ph_list)
        for purchase_history in ph_list:
            if purchase_history["quantity"] > current_stats["max_ph_quantity_readings"]:
                current_stats["max_ph_quantity_readings"] = purchase_history["quantity"]

    current_stats["last_updated"] = current_time
    with open(data_file, "w") as json_file:
        json.dump(current_stats, json_file, indent=4)
    logger.debug(json.dumps(current_stats))
    logger.info("-"*15 + "End of Periodic Processing" + "-"*15 )


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, "interval", seconds=app_config["scheduler"]["period_sec"])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8100, use_reloader=False)
