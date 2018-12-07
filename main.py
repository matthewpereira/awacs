import numpy as np
import settings

from datetime import datetime

from random import randint
from collections import defaultdict
from github import Github

from bokeh.plotting import output_file, figure, show
from bokeh.models import HoverTool
from bokeh.layouts import column


def get_prs(repo):
    pr_count = defaultdict(int)

    for prs in repo.get_pulls('all'):
        created = prs.created_at
        created = created.replace(hour=0, minute=0, second=0, microsecond=0) # squash it down to the date
        pr_count[created] += 1

    dates, occurances = list(pr_count.keys()), list(pr_count.values())

    return np.array(dates, dtype=np.datetime64), np.array(occurances), pr_count


def get_rand_color():
    return (randint(0, 255),randint(0, 255),randint(0, 255))


if __name__ == "__main__":

    g = Github(settings.GH_KEY)
    org = g.get_organization(settings.ORGANIZATION)
    repos = [org.get_repo(x) for x in settings.REPOS]

    print("Scanning data in {}".format(settings.ORGANIZATION))

    output_file("html/concourse_prs.html", title="Concourse PRs over time")

    hover = HoverTool(
        tooltips=[
            ("Repo", "@legend"),
            ("date", "@x{%F}"),
            ("# of PRs", "@y")
        ],
        formatters={"x": "datetime"}
    )
    hover.point_policy = 'snap_to_data'

    p = figure(width=1080, height=500, x_axis_type="datetime", tools=[hover])
    p2 = figure(width=1080, height=500, x_axis_type="datetime", tools=[hover])

    totals_dict = defaultdict(int)

    for repo in repos:
        print("Scanning {}".format(repo.full_name))
        array_dates, array_occurances, pr_counts = get_prs(repo)
        p.line(array_dates, array_occurances, color=get_rand_color(), legend=repo.full_name, alpha=0.8)

        for key, value in pr_counts.items():
            totals_dict[key] += value

    tx = list(totals_dict.keys())
    ty = list(totals_dict.values())
    tx, ty = zip(*sorted(zip(tx, ty)))

    pr_2018 = 0
    pr_2017 = 0
    pr_2016 = 0
    pr_2015 = 0

    for date in totals_dict.keys():

        if datetime.strptime('Jan 1 2015', '%b %d %Y') <= date < datetime.strptime('Jan 1 2016', '%b %d %Y'):
            pr_2015 += totals_dict[date]
        if datetime.strptime('Jan 1 2016', '%b %d %Y') <= date < datetime.strptime('Jan 1 2017', '%b %d %Y'):
            pr_2016 += totals_dict[date]
        if datetime.strptime('Jan 1 2017', '%b %d %Y') <= date < datetime.strptime('Jan 1 2018', '%b %d %Y'):
            pr_2017 += totals_dict[date]
        if datetime.strptime('Jan 1 2018', '%b %d %Y') <= date < datetime.strptime('Jan 1 2019', '%b %d %Y'):
            pr_2018 += totals_dict[date]

    print(pr_2015)
    print(pr_2016)
    print(pr_2017)
    print(pr_2018)

    totals_x = np.array(tx, dtype=np.datetime64)
    totals_y = np.array(ty)
    p2.line(totals_x, totals_y, color="firebrick", legend="Total PRs")

    p.title.text = "PRs for {} over time".format(settings.ORGANIZATION)
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'PRs'
    p.ygrid.band_fill_color = "olive"
    p.ygrid.band_fill_alpha = 0.1

    p2.title.text = "PR Volume for {} over time".format(settings.ORGANIZATION)
    p2.legend.location = "top_left"
    p2.grid.grid_line_alpha = 0
    p2.xaxis.axis_label = 'Date'
    p2.yaxis.axis_label = 'PRs'
    p2.ygrid.band_fill_color = "olive"
    p2.ygrid.band_fill_alpha = 0.1

    show(column(p, p2))


