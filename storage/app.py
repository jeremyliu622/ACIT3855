import logging, logging.config
import yaml
import json
import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from book_inventory import BookInventory
from purchase_history import PurchaseHistory
import datetime
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    db_info = app_config["db"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

DB_ENGINE = create_engine("mysql+pymysql://%s:%s@%s:%s/%s"
                          % (db_info["user"], db_info["password"], db_info["hostname"], db_info["port"], db_info["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info("Connecting to DB. Hostname: %s, Port: %s" % (db_info["hostname"], db_info["port"]))


def add_new_book(body):
    """ add a new book to the online shop inventory """

    session = DB_SESSION()

    new_book = BookInventory(
                body["book_id"],
                body["name"],
                body["author"],
                body["category"],
                body["price"],
                body["quantity"]
            )

    # print(new_book.to_dict())

    session.add(new_book)
    session.commit()
    session.close()

    logger.info("Stored event %s request with a unique id of %s" % ("adding book", body["book_id"]))

    return NoContent, 201


def purchase_book(body):
    """ purchase books from the online bookshop"""

    session = DB_SESSION()

    purchase_history = PurchaseHistory(
                        body["book_id"],
                        body["purchase_id"],
                        body["username"],
                        body["quantity"]
                    )

    session.add(purchase_history)
    session.commit()
    session.close()

    logger.info("Stored event %s request with a unique id of %s" % ("purchasing book", body["purchase_id"]))

    return NoContent, 201


def get_book_inventory(start_timestamp, end_timestamp):
    """ Get the book inventories after the timestamp """

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    book_inventories = session.query(BookInventory).filter(
        and_(BookInventory.date_created >= start_timestamp_datetime,
             BookInventory.date_created < end_timestamp_datetime))
    results_list = []

    for book_inventory in book_inventories:
        results_list.append(book_inventory.to_dict())

    session.close()

    logger.info("Query for getting Book Inventories between %s and %s returns %d results"
                % (start_timestamp_datetime, end_timestamp_datetime, len(results_list)))

    return results_list, 200


def get_purchase_history(start_timestamp, end_timestamp):
    """ Get the purchase histories after the timestamp """

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    purchase_histories = session.query(PurchaseHistory).filter(
        and_(PurchaseHistory.date_created >= start_timestamp_datetime,
             PurchaseHistory.date_created < end_timestamp_datetime))
    results_list = []

    for purchase_history in purchase_histories:
        results_list.append(purchase_history.to_dict())

    session.close()

    logger.info("Query for getting Purchase Histories between %s and %s returns %d results"
                % (start_timestamp_datetime, end_timestamp_datetime, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """
    print("process start")
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "bi":
            add_new_book(payload)
        elif msg["type"] == "ph":
            purchase_book(payload)
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)

