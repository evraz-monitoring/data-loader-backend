from data_loader.consumer import TopicConsumer
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Description of the command"

    def handle(self, *args, **options):
        consumer = TopicConsumer(
            [settings.KAFKA_BROKER_URL], settings.KAFKA_METRICS_TOPIC
        )
        consumer.consume_messages()
