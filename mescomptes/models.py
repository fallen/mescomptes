from django.db import models


class Devise(models.Model):
    name = models.TextField(unique=True)
    symbol = models.TextField()

    def __str__(self):
        return self.name + " (" + self.symbol + ")"


class Compte(models.Model):
    name = models.TextField(unique=True)
    opening_date = models.DateField()
    opening_balance = models.FloatField(default=0, blank=True, null=True)
    models.FloatField()
    devise = models.ForeignKey(Devise)

    def __str__(self):
        return self.name


class Categorie(models.Model):
    name = models.TextField(unique=True)
    mensualiser = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Inscription(models.Model):
    date = models.DateField()
    credit = models.FloatField(default=0, blank=True, null=True)
    debit = models.FloatField(default=0, blank=True, null=True)
    libelle = models.TextField(blank=True)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    categorie = models.ManyToManyField(Categorie, blank=True)

    def __str__(self):
        return "{}: {} debit: {} credit: {}".format(self.date, self.libelle, self.debit, self.credit)
