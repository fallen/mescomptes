from django.db import models


class Devise(models.Model):
    name = models.TextField(unique=True)
    symbol = models.TextField()

    def __str__(self):
        return self.name + " (" + self.symbol + ")"


class Compte(models.Model):
    name = models.TextField(unique=True)
    opening_date = models.DateField()
    opening_balance = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=20)
    models.DecimalField()
    devise = models.ForeignKey(Devise, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Regex(models.Model):
    expr = models.TextField()

    def __str__(self):
        return self.expr

class Categorie(models.Model):
    name = models.TextField(unique=True)
    mensualiser = models.BooleanField(default=False)
    regexs = models.ManyToManyField(Regex)

    def __str__(self):
        return self.name


class Inscription(models.Model):
    date = models.DateField()
    credit = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=20)
    debit = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=20)
    libelle = models.TextField(blank=True)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    categorie = models.ManyToManyField(Categorie, blank=True)

    def __str__(self):
        return "{}: {} debit: {} credit: {}".format(self.date, self.libelle, self.debit, self.credit)

    class Meta:
        get_latest_by = 'date'
