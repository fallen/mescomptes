import os
import argparse
import re
import sys
import subprocess
import datetime
import locale
from locale import atof


def get_parser():
    parser = argparse.ArgumentParser(description='Loads PDF from eLCL to database')
    parser.add_argument('files', help="file to load into the database", nargs='*')
    account_group = parser.add_mutually_exclusive_group(required=True)
    account_group.add_argument('--auto-detect-account', help="auto detect account name", action='store_true')
    account_group.add_argument('--account', help="set account name", action='store')
    return parser


def load_file(file, compte):
    print("on importe \'{file}\'".format(file=file))

    cmd = "pdfgrep -m 1 -o \'du [0-9]{{1,2}}\.[0-9]{{1,2}}\.[0-9]{{4}} au [0-9]{{1,2}}\.[0-9]{{1,2}}\.[0-9]{{4}}\' {file}"\
        .format(file=file)
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    timeframestr = proc.stdout

    res = re.match(
        'du (?P<jour_src>[0-9]{1,2})\.(?P<mois_src>[0-9]{1,2})\.(?P<annee_src>[0-9]{4}) au (?P<jour_dst>[0-9]{1,2})\.(?P<mois_dst>[0-9]{1,2})\.(?P<annee_dst>[0-9]{4})', timeframestr)
    if res is None:
        print("Cannot extract day/month/year from pdf file {file}".format(file=file))
        sys.exit(1)
    jour_source = res.group('jour_src')
    mois_source = res.group('mois_src')
    jour_dest = res.group('jour_dst')
    mois_dest = res.group('mois_dst')
    annee_source = res.group('annee_src')
    annee_dest = res.group('annee_dst')
    if jour_source is None or jour_dest is None or mois_source is None or mois_dest is None or annee_source is None or annee_dest is None:
        print("cannot extract day or month or year from pdf file {file}".format(file=file))
    print("Le fichier contient des données du {jour_src}.{mois_src}.{annee_src} au {jour_dst}.{mois_dst}.{annee_dst}"
          .format(jour_src=jour_source, mois_src=mois_source, jour_dst=jour_dest, mois_dst=mois_dest,
                  annee_src=annee_source, annee_dst=annee_dest))

    for year in range(int(annee_source), int(annee_dest) + 1):
        short_year = "{year:d}".format(year=(int(year) % 100))
        if year == int(annee_source):
            mois_depart = int(mois_source)
        else:
            mois_depart = 1
        if year == int(annee_dest):
            mois_fin = int(mois_dest)
        else:
            mois_fin = 12
        for mois in range(int(mois_depart), int(mois_fin) + 1):
            if mois == int(mois_source):
                jour_depart = int(jour_source)
            else:
                jour_depart = 1
            if mois == int(mois_dest):
                jour_fin = int(jour_dest)
            else:
                jour_fin = 31
            for jour in range(jour_depart, jour_fin + 1):
                cmd = "pdfgrep '{jour:02d}\.{mois:02d}\.{year}' {file}".format(file=file, jour=jour, mois=mois,
                                                                               year=short_year)
                try:
                    proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                    output = proc.stdout
                    print("trouvé : ")
                    for line in output.splitlines():
                        res = re.match(
                            "\s+(?P<date>\d+\.\d+)\s+(?P<libelle>(\S+\s)+(\S+))\s+(?P<date2>\d+\.\d+\.\d+)\s+(?P<montant>((?:0|[1-9]\d{{0,2}}(?:\s?\d{{3}})*)(?:,\d+)?))".format(
                                jour=jour, mois=mois), line)
                        if res is not None:
                            inscription = res.groupdict()
                            print("libelle : {lib}".format(lib=inscription['libelle']))
                            print("date : {date}".format(date=inscription['date2']))
                            print("montant : {montant}".format(montant=inscription['montant']))
                            inscription['credit'] = False
                            inscription['debit'] = False
                            if len(line) < 125:
                                inscription['debit'] = True
                                print("débit")
                            elif len(line) > 130:
                                inscription['credit'] = True
                                print("crédit")
                            else:
                                print("Cannot decide whether credit or debit for line {line}".format(line=line))
                                sys.exit(1)
                            # on inject dans la base de données
                            try:
                                date2 = inscription['date2']
                                date = datetime.date(int(date2[6:8])+2000, int(date2[3:5]), int(date2[0:2]))
                                print("date: {}".format(date))
                                compte.inscription_set.create(date=date, debit=atof(inscription['montant'].replace(' ', '')) if inscription[
                                    'debit'] else None, credit=atof(inscription['montant'].replace(' ', '')) if inscription[
                                    'credit'] else None, libelle=inscription['libelle'])
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
    for file in args.files:
        if args.auto_detect_account:
            print("on auto detect le compte")
            cmd = "pdfgrep -m 1 'Compte' {file}".format(file=file)
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = proc.stdout
            res = re.match(".*Compte\s+:\s+(?P<compte>\d+\s\w).*", output)
            if res is None:
                print("auto detection of account failed!")
                sys.exit(1)
            account = res.group('compte')
        elif args.account is None:
            print("please either use --auto-detect-account or select account via --account")
            sys.exit(1)
        else:
            account = args.account
        print("compte : {compte}".format(compte=account))
        try:
            compte = Compte.objects.get(name=account)
        except Compte.DoesNotExist:
            print("The account {account} does not exist".format(account=account))
            sys.exit(1)
        load_file(file, compte)


if __name__ == "__main__":
    main()
