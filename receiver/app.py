import logging, logging.config
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


def add_new_book(body):
    """add a new book to the online bookstore"""

    logger.info("Received event %s request with a unique id of %s"
                % ("adding book", body["book_id"]))

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
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

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
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
