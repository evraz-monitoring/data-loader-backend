import redis
import json
import logging
from kafka import KafkaConsumer

logger = logging.getLogger('main')


class MultiTopicConsumer:
    def __init__(self, brokers, topics):
        self.brokers = brokers
        self.topics = topics
        self.consumer = KafkaConsumer(bootstrap_servers=self.brokers,
                                      auto_offset_reset='latest',
                                      enable_auto_commit=True)
        self.consumer.subscribe(self.topics)
        self.redis = redis.Redis(host="localhost")

    def consume_messages(self):
        while True:
            for msg in self.consumer:
                logger.info("Received message: topic=%s, partition=%d, offset=%d, ts=%s, value=%s",
                            msg.topic, msg.partition, msg.offset, msg.timestamp, msg.value)
                self.add_data_to_cache(msg)

    def add_data_to_cache(self, message):
        data = {
            "value": json.loads(message.value)['value'],
            "ts": message.timestamp
        }
        self.redis.hset("measures", message.topic, json.dumps(data))
