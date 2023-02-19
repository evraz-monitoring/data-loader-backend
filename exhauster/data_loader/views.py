import json
from collections import defaultdict
from datetime import datetime

import redis
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseNotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from .serializers import ExhausterSerializer, MetricSerializer, SinterMachineSerializer


class Metrics(APIView):
    def get(self, request):
        metrics = models.Metric.objects.all()
        if not metrics:
            return HttpResponseNotFound()

        serialized_metrics = MetricSerializer(metrics, many=True)
        return Response(serialized_metrics.data)


class Exhausters(APIView):
    def get(self, request, pk=None):
        if pk is None:
            exhausters = models.Exhauster.objects.all()
        else:
            exhausters = models.Exhauster.objects.filter(pk=pk)
        if not exhausters:
            return HttpResponseNotFound()

        serialized_exhausters = ExhausterSerializer(exhausters, many=True)
        return Response(serialized_exhausters.data)


class SinterMachines(APIView):
    def get(self, request):
        sinter_machines = models.SinterMachine.objects.all()
        if not sinter_machines:
            return HttpResponseNotFound()
        serialized_sinter_machines = SinterMachineSerializer(sinter_machines, many=True)
        return Response(serialized_sinter_machines.data)


class ActualSystemIndicators(APIView):
    def get(self, request):
        redis_ = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        keys = redis_.keys(pattern="metric:*")
        values = redis_.mget(keys)
        result = defaultdict(dict)
        for key, value in zip(keys, values):
            _, exhauster, metric = key.decode("utf-8").split(":")
            value = json.loads(value)
            result[str(exhauster)][metric] = {"value": value["v"], "ts": value["ts"]}
        return Response(result)


class HistoricalSystemIndicator(APIView):
    def get(self, request):
        date_from = datetime.fromisoformat(request.query_params["dateFrom"][:-1])
        date_to = datetime.fromisoformat(request.query_params["dateTo"][:-1])
        metrics = request.query_params["metrics"].split(",")
        exhauster_id = request.query_params["exhauster"]
        metrics_qs = models.Metric.objects.filter(name__in=metrics)
        system_indicators = models.SystemIndicator.objects.select_related(
            "metric"
        ).filter(
            Q(measurement_time__gte=date_from)
            & Q(measurement_time__lte=date_to)
            & Q(metric__in=metrics_qs, exhauster_id=exhauster_id)
        )
        if not system_indicators:
            return HttpResponseNotFound()

        result = defaultdict(dict)
        for indicator in system_indicators:
            result[str(indicator.measurement_time.timestamp())][
                indicator.metric.name
            ] = indicator.value
        return Response(result)
