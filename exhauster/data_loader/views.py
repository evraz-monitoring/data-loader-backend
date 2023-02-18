from collections import defaultdict
from datetime import datetime

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
        actual_ts = models.SystemIndicator.objects.latest(
            "measurement_time"
        ).measurement_time
        indicators = models.SystemIndicator.objects.select_related("metric").filter(
            measurement_time=actual_ts
        )
        result = []
        exhausters = models.Exhauster.objects.all()
        if not indicators:
            return HttpResponseNotFound
        for exhauster in exhausters:
            data = {"exhauster": exhauster.pk, "ts": actual_ts.timestamp()}
            exhauster_indicators = indicators.filter(exhauster=exhauster)
            metrics = {
                indicator.metric.name: indicator.value
                for indicator in exhauster_indicators
            }
            data.update(metrics)
            result.append(data)
        return Response(result)


class HistoricalSystemIndicator(APIView):
    def get(self, request):
        date_from = datetime.fromisoformat(request.query_params["dateFrom"])
        date_to = datetime.fromisoformat(request.query_params["dateTo"])
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
            return HttpResponseNotFound

        result = defaultdict(dict)
        for indicator in system_indicators:
            result[str(indicator.measurement_time.timestamp())][
                indicator.metric.name
            ] = indicator.value
        return Response(result)
