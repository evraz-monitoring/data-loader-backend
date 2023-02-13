

from django.core.management.base import BaseCommand

from data_loader.consumer import MultiTopicConsumer


class Command(BaseCommand):
    help = 'Description of the command'

    def handle(self, *args, **options):
        # Your command logic goes here
        consumer = MultiTopicConsumer(["0.0.0.0:9092"], ["measure1", "measure2", "measure3"])
        consumer.consume_messages()

