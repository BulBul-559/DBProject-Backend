from django.db import models

# Create your models here.

class Sduter(models.Model):
    # username = models.CharField(max_length=20)
    sdut_id = models.CharField(max_length=20)
    name = models.CharField(max_length=20,null=True)
    college = models.CharField(max_length=20,null=True)
    class_number = models.CharField(max_length=20,null=True)
    identity = models.IntegerField()

class Youtholer(models.Model):
    sdut_id = models.CharField(max_length=20)
    name = models.CharField(max_length=20,null=True)
    department = models.CharField(max_length=20,null=True)
    identity = models.IntegerField()

class DutyList(models.Model):
    sdut_id = models.CharField(max_length=20)
    day = models.IntegerField()
    frame = models.IntegerField()

class DutyNow(models.Model):
    sdut_id = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    duty_state = models.CharField(max_length=20)

class DutyHistory(models.Model):
    sdut_id = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    totlal_time = models.IntegerField()
    duty_state = models.CharField(max_length=20)