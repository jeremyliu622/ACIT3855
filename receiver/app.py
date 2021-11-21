import logging, logging.config
import connexion
import yaml
from connexion import NoContent
import time
import datetime
import json
from pykafka import KafkaClient

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

HEADERS = {"content-type": "application/json"}

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    max_retry_count = app_config["events"]["max_retry_count"]
    sleep_time = app_config["events"]["sleep_time"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

current_retry_count = 0
while current_retry_count < max_retry_count:
    logger.info("Trying to connect to Kafka - current retry count: %d." % current_retry_count)
    try:
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()
        
        logger.info("Successfully connect to Kafka.")
        break
    except:
        logger.error("Failed to connect to Kafka.")
        time.sleep(sleep_time)
        current_retry_count += 1


def add_new_book(body):
    """add a new book to the online bookstore"""

    logger.info("Received event %s request with a unique id of %s"
                % ("adding book", body["book_id"]))

    msg = {
        "type": "bi",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event %s response %s"
                % ("adding book", body["book_id"]))

    return NoContent, 201


def purchase_book(body):
    """purchase a book from the online bookstore"""

    logger.info("Received event %s request with a unique id of %s"
                % ("purchasing book", body["purchase_id"]))

    msg = {
        "type": "ph",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event %s response %s"
                % ("purchasing book", body["purchase_id"]))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':
    app.run(port=8080)
