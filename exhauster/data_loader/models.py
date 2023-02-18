from django.db import models

# from timescale.fields import TimescaleDateTimeField
# Create your models here.


class SinterMachine(models.Model):
    id = models.IntegerField(primary_key=True, null=False)


class Metric(models.Model):
    name = models.CharField(max_length=256)
    measure = models.CharField(max_length=10, default="")


class Exhauster(models.Model):
    serviceability = models.BooleanField(default=True)
    last_replacement_date = models.DateField()
    sinter_machine = models.ForeignKey(SinterMachine, on_delete=models.CASCADE)


class SystemIndicator(models.Model):
    measurement_time = models.DateTimeField(primary_key=True)
    value = models.FloatField()
    exhauster = models.ForeignKey(Exhauster, on_delete=models.CASCADE)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "data_loader_systemindicator"
        unique_together = (("measurement_time", "exhauster_id", "metric_id"),)
