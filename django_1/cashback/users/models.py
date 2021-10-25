from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    adress = models.CharField(max_length=200)
    doctor_count = models.IntegerField()

class Polzovatel(models.Model):
    email = models.EmailField()
    reg_date = models.DateTimeField()
    points = models.IntegerField()
    fav_hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, related_name='users_added_as_fav')

    


