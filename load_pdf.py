import os
import argparse
import re
import sys
import subprocess
import datetime
import locale
from locale import atof


def get_parser():
    parser = argparse.ArgumentParser(description='Loads PDF from LCL/eLCL to database')
    parser.add_argument('files', help="file to load into the database", nargs='*')
    account_group = parser.add_mutually_exclusive_group(required=True)
    account_group.add_argument('--auto-detect-account', help="auto detect account name", action='store_true')
    account_group.add_argument('--account', help="set account name", action='store')
    return parser


def load_file(filepath, compte):
    print("Importing \'{filepath}\'".format(filepath=filepath))

    # Long dates: 30.12.2018
    date_re = "[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}"
    date_format = "%d.%m.%Y"

    # Short dates: 30.12.18
    shortdate_re = "[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2}"
    shortdate_format = "%d.%m.%y"

    # Money amount: 4 321,42
    montant_re = "((?:0|[1-9]\d{0,2}(?:\s?\d{3})*)(?:,\d+)?)"

    cmd = "pdfgrep -m 1 -o \'du {date_re} au {date_re}\' {filepath}".format(filepath=filepath, date_re=date_re)
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = proc.stdout

    res = re.match('du (?P<date_src>{date_re}) au (?P<date_dst>{date_re})'.format(date_re=date_re), output)
    if res is None:
        print("Cannot extract day/month/year from pdf file {filepath}".format(filepath=filepath))
        sys.exit(1)
    date_src = datetime.datetime.strptime(res.group('date_src'), date_format).date()
    date_dst = datetime.datetime.strptime(res.group('date_dst'), date_format).date()
    print("Le fichier contient des données du {date_src} au {date_dst}".format(date_src=date_src, date_dst=date_dst))

    cmd = "pdfgrep '  {date}' {filepath}".format(filepath=filepath, date=shortdate_re)
    proc = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, universal_newlines=True)
    output = proc.stdout
    for line in output.splitlines():
        regexp = "^\s+(?P<ignored_date>\d+\.\d+)\s+(?P<libelle>(\S+\s)+(\S+))\s+(?P<date>{date_re})(?P<spacing>[\s.]+)(?P<montant>{montant_re})(?P<more_spacing>\s*\.?)$".format(date_re=shortdate_re, montant_re=montant_re)
        res = re.match(regexp, line)
        if res is not None:
            # print("Following line successfully parsed: '{}'".format(line))
            inscription = res.groupdict()
            spacing = inscription['spacing']
            credit = False
            debit = False
            if len(spacing) < 20:
                debit = True
            elif len(spacing) > 30:
                credit = True
            else:
                raise ValueError("Cannot decide whether credit or debit for line {line}".format(line=line))
            date = datetime.datetime.strptime(inscription['date'], shortdate_format).date()
            montant = atof(inscription['montant'].replace(' ', ''))
            # Inject in database
            compte.inscription_set.create(
                    date=date,
                    debit=montant if debit else None,
                    credit=montant if credit else None,
                    libelle=inscription['libelle'])


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comptes.settings")
    import django
    django.setup()
    locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
    from mescomptes.models import Compte
    parser = get_parser()
    args = parser.parse_args()
    for filepath in args.files:
        print("Importing \'{filepath}\'".format(filepath=filepath))
        if args.auto_detect_account:
            print("on auto detect le compte")
            cmd = "pdfgrep -m 1 'Compte : [0-9]+ [a-zA-Z]' {filepath}".format(filepath=filepath)
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = proc.stdout
            res = re.match(".*Compte\s+:\s+(?P<compte>\d+\s\w).*", output)
            if res is None:
                print("auto detection of account failed!")
                sys.exit(1)
            account = res.group('compte')
        elif args.account is None:
            print("Please either use --auto-detect-account or select account via --account")
            sys.exit(1)
        else:
            account = args.account
        print("Compte : {compte}".format(compte=account))
        try:
            compte = Compte.objects.get(name=account)
        except Compte.DoesNotExist:
            print("The account {account} does not exist".format(account=account))
            sys.exit(1)
        load_file(filepath, compte)


if __name__ == "__main__":
    main()
