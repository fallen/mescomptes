import locale
import os
import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="get each month debits")
    parser.add_argument("--year", required=True)
    parser.add_argument("--compte", required=True)
    return parser


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comptes.settings")
    import django
    django.setup()
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
    from mescomptes.models import Compte

    parser = get_parser()
    args = parser.parse_args()

    compte = Compte.objects.get(name=args.compte)

    debits = {}
    for month in range(1, 13):
        debit = 0
        inscriptions = compte.inscription_set.filter(date__year=args.year).filter(date__month=month).filter(debit__gte=0)
        for inscription in inscriptions:
            debit = debit + inscription.debit
        debits[month] = debit

    print("debits : {}".format(debits))


if __name__ == "__main__":
    main()