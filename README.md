# Mescomptes

Outil de gestion de comptes.

Permet pour l'instant de charger les PDF LCL/eLCL dans la base de données et de requêter via django.contrib.admin ou en cmdline via l'ORM Django via
```bash
$ python3 manage.py shell
```

exemple : 
```python
$ python3 manage.py shell
Python 3.6.5 (default, Apr  1 2018, 05:46:30) 
[GCC 7.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from mescomptes.models import Inscription
>>> from django.db.models import Sum, Avg
>>> Inscription.objects.filter(libelle__contains='CB LE PETIT CARILLO').aggregate(Sum('debit'), Avg('debit'))
{'debit__sum': 488.25, 'debit__avg': 24.4125}
```
