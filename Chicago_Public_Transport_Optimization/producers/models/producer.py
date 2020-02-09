"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)


class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        self.broker_properties = {
            "bootstrap.servers": "localhost:9092, localhost:9093, localhost:9093",
            "schema.registry.url": "http://localhost:8081"

        }

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        self.producer = AvroProducer(
            self.broker_properties,
            default_key_schema=self.key_schema,
            default_value_schema=self.value_schema
        )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        client = AdminClient({"bootstrap.servers": self.broker_properties["bootstrap.servers"]})
        exists = self.topic_exists(client, self.topic_name)

        if exists is True:
            logger.info(f"topic {self.topic_name} already exists. No topic is created!")
            return
        else:
            logger.info(f"creating {self.topic_name} topic...")
            topic = client.create_topics([
                NewTopic(topic=self.topic_name, num_partitions=self.num_partitions, replication_factor=self.num_replicas)
            ])
            for _, future in topic.items():
                try:
                    future.result(timeout=10)
                    logger.info(f"topic {self.topic_name} is created")
                except Exception as e:
                    logger.fatal(f"failed to create topic {self.topic_name}: {e}")

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        logger.info("flushing producer...")
        self.producer.flush()
        logger.info("producer closed")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))

    def topic_exists(self, client, topic_name):
        topic_metadata = client.list_topics(timeout=5).topics.get(topic_name)
        return topic_metadata is not None
