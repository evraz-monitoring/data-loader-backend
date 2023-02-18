import json
import logging
import ssl
from datetime import datetime

import redis
from data_loader.models import Exhauster, Metric, SystemIndicator
from django.conf import settings
from kafka import KafkaConsumer

logger = logging.getLogger("main")


class TopicConsumer:
    def __init__(self, brokers, topic):
        self.brokers = brokers
        self.topic = topic
        context = ssl.create_default_context(cafile=settings.CA_PATH)
        self.consumer = KafkaConsumer(
            self.topic,
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
        self.redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        with open(settings.MAPPING_PATH, "r", encoding="utf-8") as f:
            self.mapping_dict = json.load(f)

        self.metrics_mapping = {
            name: id_ for id_, name in Metric.objects.all().values_list("id", "name")
        }

    def consume_messages(self):
        while True:
            for msg in self.consumer:
                self._add_measures(msg.value)
                self._add_data_to_queue(
                    settings.REDIS_QUEUE_NAME,
                    self._parse_message(msg.value, msg.timestamp),
                )

    def _parse_message(self, message, timestamp):
        with open(settings.MAPPING_PATH, "r", encoding="utf-8") as f:
            mapping_dict = json.load(f)
        exhausters = Exhauster.objects.all()

        result = [
            {"exhauster": exhauster.pk, "ts": timestamp} for exhauster in exhausters
        ]
        for measure, value in message.items():
            if measure in mapping_dict:
                met_name = mapping_dict[measure]["metric"]
                exhauster_id = mapping_dict[measure]["exhauster"]
                result[exhauster_id - 1][met_name] = value
        return result

    def _add_data_to_cache(self, message):
        data = {"value": json.loads(message.value)["value"], "ts": message.timestamp}
        self.redis.hset("measures", message.topic, json.dumps(data))

    def _add_data_to_queue(self, channel, message):
        self.redis.publish(channel, json.dumps(message))

    def _add_measures(self, measures):
        ts = datetime.fromisoformat(measures["moment"])
        system_indicators = []
        for measure, value in measures.items():
            if measure not in self.mapping_dict:
                continue
            met_name = self.mapping_dict[measure]["metric"]
            system_indicators.append(
                SystemIndicator(
                    measurement_time=ts,
                    value=value,
                    exhauster_id=self.mapping_dict[measure]["exhauster"],
                    metric_id=self.metrics_mapping[met_name],
                )
            )
        SystemIndicator.objects.bulk_create(system_indicators, ignore_conflicts=True)

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
