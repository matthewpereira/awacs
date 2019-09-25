import numpy as np
import pandas as pd
import settings
import matplotlib.pyplot as plt
import sys, getopt
import argparse

from collections import defaultdict
from github import Github

def get_prs(repo, pivotal_members, show_pivots):
    pr_count = defaultdict(int)

    for prs in repo.get_pulls('all'):

        if is_pivot(prs.user.login, pivotal_members) and not show_pivots:
            continue

        created = prs.created_at
        created = created.replace(hour=0, minute=0, second=0, microsecond=0) # squash it down to the date
        pr_count[created] += 1

    dates, occurances = list(pr_count.keys()), list(pr_count.values())

    return np.array(dates, dtype=np.datetime64), np.array(occurances), pr_count


def is_pivot(login, pivotal_member):
    for member in pivotal_member:
        if login == member.login:
            return True
        if login == 'dependabot':
            return True

    return False

def show_pivots(opts): 
    return opts.show_pivots

def process_arguments():
    parser = argparse.ArgumentParser(description='Process a git repo and graph the PRs. See README.md for setup instructions.')
    parser.add_argument('-sp', '--show-pivots', action='store_true', help='include pivotal contributions')

    args = parser.parse_args()
    
    return args

def print_results(monthly, yearly): 
    monthlySum = monthly.sum()
    yearlySum = yearly.sum()

    print("\nPrinting PRs per month:")
    print(monthlySum.to_string())
    print("")
    print("\nPrinting PRs per year:")
    print(yearlySum.to_string())

if __name__ == "__main__":

    cli_arguments = process_arguments()
    show_pivots = show_pivots(cli_arguments)
    
    g = Github(settings.GH_KEY)
    org = g.get_organization(settings.ORGANIZATION)
    
    pivotal_members = []

    for team in org.get_teams():
        if team.name == 'Pivotal':
            pivotal_members = [member for member in team.get_members()]

    repos = [org.get_repo(x) for x in settings.REPOS]

    print("Scanning data in {}".format(settings.ORGANIZATION))

    totals_dict = defaultdict(int)
    
    for repo in repos:
        print("Scanning {}".format(repo.full_name))

        array_dates, array_occurances, pr_counts = get_prs(repo, pivotal_members, show_pivots)

        for key, value in pr_counts.items():
            totals_dict[key] += value

    df = pd.DataFrame(totals_dict.items())
    df.columns = ['Date', 'PRs']
    df = df.set_index(df['Date'])
    df.index = pd.to_datetime(df.index)

    monthly = df.groupby(pd.Grouper(freq="M")) 
    yearly  = df.groupby(pd.Grouper(freq="Y"))
    
    print_results(monthly, yearly)

    plt.figure(figsize=(12, 16), dpi=600)

    ax = monthly.sum().plot.line()
    ax = yearly.sum().plot.line()

    ax.set_title("# of community Concourse PRs over time")
    ax.set_ylabel("# PRs per month")
    ax.set_xlabel("Date")
    ax.grid()

    plt.savefig('test.png', dpi=600)
    plt.show()
