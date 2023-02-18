import json
import logging
import ssl
from datetime import datetime

import redis
from data_loader.models import Exhauster, Metric, SystemIndicator
from django.conf import settings
from kafka import KafkaConsumer, TopicPartition

logger = logging.getLogger("main")


class TopicConsumer:
    def __init__(self, brokers, topic):
        self.brokers = brokers
        self.topic = topic
        context = ssl.create_default_context(cafile=settings.CA_PATH)
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.brokers,
            security_protocol="SASL_SSL",
            ssl_context=context,
            sasl_mechanism="SCRAM-SHA-512",
            sasl_plain_username=settings.KAFKA_USERNAME,
            sasl_plain_password=settings.KAFKA_PASSWORD,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("ascii")),
        )
        self.redis = redis.Redis(host="localhost")

    def consume_messages(self):
        self.consumer.assign([TopicPartition(topic=self.topic, partition=0)])
        self.consumer.seek_to_beginning()
        while True:
            for msg in self.consumer:
                logger.info(
                    "Received message: topic=%s, partition=%d, offset=%d, ts=%s, value=%s",  # noqa: E501
                    msg.topic,
                    msg.partition,
                    msg.offset,
                    msg.timestamp,
                    msg.value,
                )
                self._add_measures(msg.value)

    def _add_data_to_cache(self, message):
        data = {"value": json.loads(message.value)["value"], "ts": message.timestamp}
        self.redis.hset("measures", message.topic, json.dumps(data))

    def _add_measures(self, measures):
        with open(settings.MAPPING_PATH, "r", encoding="utf-8") as f:
            mapping_dict = json.load(f)
        ts = datetime.fromisoformat(measures["moment"])
        exhausters = Exhauster.objects.all()
        metrics = Metric.objects.all()
        system_indicators = []
        for measure, value in measures.items():
            if measure in mapping_dict:
                met_name = mapping_dict[measure]["metric"]
                exhauster = exhausters.get(id=mapping_dict[measure]["exhauster"])
                metric = metrics.filter(name=met_name)[0]
                system_indicators.append(
                    SystemIndicator(
                        measurement_time=ts,
                        value=value,
                        exhauster=exhauster,
                        metric=metric,
                    )
                )
        SystemIndicator.objects.bulk_create(system_indicators)

        logger.info(" measure load to database")

    def _add_metrics(self, value):
        with open(settings.MAPPING_PATH, "r", encoding="utf-8") as f:
            mapping_dict = json.load(f)
        metrics = []
        del value["moment"]
        for name in value.keys():
            if name in mapping_dict:
                met_name = mapping_dict[name]
                metrics.append(Metric(name=met_name["metric"]))

        Metric.objects.bulk_create(metrics)
