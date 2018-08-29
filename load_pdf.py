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
    cmd = "pdfgrep -m 1 -o \'du [0-9]{{1,2}}\.[0-9]{{1,2}}\.[0-9]{{4}} au [0-9]{{1,2}}\.[0-9]{{1,2}}\.[0-9]{{4}}\' {filepath}"\
        .format(filepath=filepath)
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    timeframestr = proc.stdout

    res = re.match(
        'du (?P<day_src>[0-9]{1,2})\.(?P<month_src>[0-9]{1,2})\.(?P<year_src>[0-9]{4}) au (?P<day_dst>[0-9]{1,2})\.(?P<month_dst>[0-9]{1,2})\.(?P<year_dst>[0-9]{4})', timeframestr)
    if res is None:
        print("Cannot extract day/month/year from pdf file {filepath}".format(filepath=filepath))
        sys.exit(1)
    day_src = int(res.group('day_src'))
    day_dst = int(res.group('day_dst'))
    month_src = int(res.group('month_src'))
    month_dst = int(res.group('month_dst'))
    year_src = int(res.group('year_src'))
    year_dst = int(res.group('year_dst'))
    print("Le fichier contient des données du {day_src}.{month_src}.{year_src} au {day_dst}.{month_dst}.{year_dst}"
          .format(day_src=day_src, day_dst=day_dst,
                  month_src=month_src, month_dst=month_dst,
                  year_src=year_src, year_dst=year_dst))

    for year in range(year_src, year_dst + 1):
        short_year = "{year:d}".format(year=(year % 100))
        month_beg = month_src if year == year_src else 1
        month_end = month_dst if year == year_dst else 12
        for month in range(month_beg, month_end + 1):
            day_beg = day_src if month == month_src else 1
            day_end = day_dst if month == month_dst else 31
            for day in range(day_beg, day_end + 1):
                cmd = "pdfgrep '{day:02d}\.{month:02d}\.{year}' {filepath}".format(filepath=filepath, day=day, month=month,
                                                                               year=short_year)
                try:
                    proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                    output = proc.stdout
                    for line in output.splitlines():
                        res = re.match(
                            "\s+(?P<date>\d+\.\d+)\s+(?P<libelle>(\S+\s)+(\S+))\s+(?P<date2>\d+\.\d+\.\d+)\s+(?P<montant>((?:0|[1-9]\d{{0,2}}(?:\s?\d{{3}})*)(?:,\d+)?))".format(day=day, month=month), line)
                        if res is not None:
                            inscription = res.groupdict()
                            print("libelle : {lib}".format(lib=inscription['libelle']))
                            print("date : {date}".format(date=inscription['date2']))
                            print("montant : {montant}".format(montant=inscription['montant']))
                            credit = False
                            debit = False
                            if len(line) < 125:
                                debit = True
                            elif len(line) > 130:
                                credit = True
                            else:
                                print("Cannot decide whether credit or debit for line {line}".format(line=line))
                                sys.exit(1)
                            # Inject in database
                            try:
                                date2 = inscription['date2']
                                date = datetime.date(int(date2[6:8])+2000, int(date2[3:5]), int(date2[0:2]))
                                print("date: {}".format(date))
                                montant = atof(inscription['montant'].replace(' ', ''))
                                compte.inscription_set.create(
                                        date=date,
                                        debit=montant if debit else None,
                                        credit=montant if credit else None,
                                        libelle=inscription['libelle'])
                            except Exception as e:
                                print("ouille : {}".format(e))
                                sys.exit(1)
                except:
                    continue


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
