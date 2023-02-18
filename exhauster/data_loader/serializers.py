from data_loader import models
from rest_framework import serializers


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Metric
        fields = ["pk", "name", "measure"]


class ExhausterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exhauster
        fields = ["pk", "serviceability", "last_replacement_date", "sinter_machine"]


class SystemIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemIndicator
        fields = [
            "pk",
            "measurement_time",
            "value",
            "sinter_machine",
            "exhauster",
            "metric",
        ]


class SinterMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SinterMachine
        fields = ["id"]
