import os
import argparse
import re
import sys
import subprocess
import datetime
import locale
from locale import atof


def get_parser():
    parser = argparse.ArgumentParser(description='Assign categories to account inscriptions')
    parser.add_argument('--category', '-c', help="category name", action='store')
    parser.add_argument('--regex', '-r', help="regex string", action='store')
    parser.add_argument('--account', '-a', help="set account name", action='store')
    parser.add_argument('--new', '-n', help="Create a new category", default=False, action="store_true")
    parser.add_argument('--list', '-l', help="List inscriptions that match the Category regexps", default=False, action="store_true")
    parser.add_argument('--add', help="Add the regex to the Category", default=False, action="store_true")
    parser.add_argument("--set-category", help="Set category to matching Inscriptions", default=False, action="store_true")
    return parser

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comptes.settings")
    import django
    django.setup()
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
    from mescomptes.models import Compte, Categorie, Regex, Inscription
    parser = get_parser()
    args = parser.parse_args()
    category = None

    if args.account is None:
        print("Please select account via --account")
        sys.exit(1)
    
    account = args.account
    print("Compte : {compte}".format(compte=account))

    try:
        compte = Compte.objects.get(name=account)
    except Compte.DoesNotExist:
        print("The account {account} does not exist".format(account=account))
        sys.exit(1)

    if args.category is None and args.set_category:
        print("Please specify a category via --category")
        sys.exit(1)

    if args.new:
        category = Categorie.objects.create(name=args.category)
    else:
        try:
            category = Categorie.objects.get(name=args.category)
            print("Category: {}".format(category))
        except Categorie.DoesNotExist:
            print("Category {} does not exist, use --new to create it".format(args.category))

    if args.regex and args.add:
        if args.add:
            regex = Regex.objects.create(expr=args.regex)
        else:
            regex = Regex.objects.get(expr=args.regex)

        if args.add:
            print("Adding regex {}".format(regex))
            category.regexs.add(regex)
            category.save()

    if args.list:
        inscriptions = []
        debit_sum = 0
        credit_sum = 0
        if category:
            regexs = list(category.regexs.all())
        else:
            regexs = [Regex(expr=args.regex)]

        for r in regexs:
            ins = Inscription.objects.filter(compte=compte, libelle__regex=r.expr).all()
            inscriptions += list(ins)
        for i in inscriptions:
            if i.debit:
                debit_sum += i.debit
            if i.credit:
                credit_sum += i.credit
            print("{}".format(i))
        print("total debit: {}".format(debit_sum))
        print("total credit: {}".format(credit_sum))

    if args.set_category:
        regexs = list(category.regexs.all())
        inscriptions = []

        for r in regexs:
            ins = Inscription.objects.filter(compte=compte, libelle__regex=r.expr).all()
            inscriptions += list(ins)

        for i in inscriptions:
            if category not in i.categorie.all():
                print("Adding {} to category {}".format(i.libelle, category))
                i.categorie.add(category)
                i.save()
        
if __name__ == "__main__":
    main()
