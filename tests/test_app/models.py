from django.db import models


class NotADjangoModel(object):
    pass


class InspectModel(models.Model):
    int = models.IntegerField()
    char = models.CharField()
    text = models.TextField()
    direct_fk = models.ForeignKey("DirectFK", on_delete=models.CASCADE)
    many_to_many = models.ManyToManyField("AnotherManyToMany")


class FK(models.Model):
    inspect_model = models.ForeignKey(InspectModel, on_delete=models.CASCADE)


class AnotherFK(models.Model):
    inspect_model = models.ForeignKey(InspectModel, on_delete=models.CASCADE)


class DirectFK(models.Model):
    bigint = models.BigIntegerField()
    boolean = models.BooleanField()


class ManyToMany(models.Model):
    inspect_model = models.ManyToManyField(InspectModel)


class AnotherManyToMany(models.Model):
    some_item = models.ForeignKey("SomeItem", on_delete=models.CASCADE)


class SomeItem(models.Model):
    date = models.DateField()
    decimal = models.DecimalField()
