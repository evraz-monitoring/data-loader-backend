

from django.core.management.base import BaseCommand

from data_loader.consumer import TopicConsumer


class Command(BaseCommand):
    help = 'Description of the command'

    def handle(self, *args, **options):
        # Your command logic goes here
        consumer = TopicConsumer(["rc1a-b5e65f36lm3an1d5.mdb.yandexcloud.net:9091"], "zsmk-9433-dev-01")
        consumer.consume_messages()

