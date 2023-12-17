from django.db import models

# Create your models here.

class Sduter(models.Model):
    # username = models.CharField(max_length=20)
    sdut_id = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=20,null=True)
    college = models.CharField(max_length=20,null=True)
    grade = models.CharField(max_length=20,null=True)
    identity = models.CharField(max_length=20,null=True)
    phone = models.CharField(max_length=20,null=True)
 

class Youtholer(models.Model):
    sdut_id = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=20,null=True)
    department = models.CharField(max_length=20,null=True)
    identity = models.CharField(max_length=20,null=True)

class DutyList(models.Model):
    sdut_id = models.CharField(max_length=20, db_index=True)
    day = models.IntegerField( db_index=True)
    frame = models.IntegerField()

class DutyNow(models.Model):
    sdut_id = models.CharField(max_length=20, db_index=True)
    start_time = models.DateTimeField()
    duty_state = models.CharField(max_length=20)

class DutyHistory(models.Model):
    sdut_id = models.CharField(max_length=20, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    total_time = models.IntegerField()
    duty_state = models.CharField(max_length=20)

class DutyLeave(models.Model):
    sdut_id = models.CharField(max_length=20, db_index=True)
    apply_time = models.DateTimeField(db_index=True)
    leave_date = models.DateTimeField(db_index=True)
    day = models.IntegerField()
    frame = models.IntegerField()