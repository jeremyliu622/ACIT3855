import logging.config
import connexion
import yaml
from connexion import NoContent
import requests
import datetime
import json
from pykafka import KafkaClient


HEADERS = {"content-type": "application/json"}

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")


def get_book_inventory(index):
    """ Get BI Reading in History """
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving BI at index %d" % index)
    count = 0

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "bi":
                if count == index:
                    return msg["payload"], 200
                count += 1
    except:
        logger.error("No more messages found")

    logger.error("Could not find BP at index %d" % index)
    return {"message": "Not Found"}, 404


def get_purchase_history(index):
    """ Get BI Reading in History """
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving PH at index %d" % index)
    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "ph":
                if count == index:
                    return msg["payload"], 200
                count += 1

    except:
        logger.error("No more messages found")

    logger.error("Could not find PH at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':
    app.run(port=8110, use_reloader=False)
