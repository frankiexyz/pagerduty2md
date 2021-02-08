#!/usr/bin/env python

import re
import requests
import arrow
import click
import markdown


def fetch_note(incident_id, apikey):
    url = f"https://api.pagerduty.com/incidents/{incident_id}/notes"
    notes = "<br/>".join(
        [
            i["content"]
            for i in requests.get(
                url, headers={"authorization": f"Token token={apikey}"}
            ).json()["notes"]
            if i
        ]
    )
    return re.sub("\n", "<br/>", notes)


@click.command()
@click.option("--html", is_flag=True, help="Print in html")
@click.option("--teamid", required=True)
@click.option("--graph", is_flag=True, help="The oncall graph")
@click.option("--start", required=True, help="The date format in 2021-01-28T03:30:21")
@click.option("--duration", required=True, help="Duration for this query in hours")
@click.option("--apikey", required=True, help="Pagerduty API key")
def main(**kwargs):
    start = arrow.get(kwargs.get("start"))
    incident_time = {}
    end = start.shift(hours=+int(kwargs.get("duration")))
    for i in arrow.Arrow.span_range("hour", start.shift(hours=-1), end.shift(hours=+1)):
        incident_time[i[0].format("YYYY-MM-DDTHH:mm:ss")] = 0
    if arrow.utcnow() < end:
        end = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")
    start = arrow.get(kwargs.get("start")).format("YYYY-MM-DDTHH:mm:ss")
    teamid = kwargs.get("teamid")
    apikey = kwargs.get("apikey")
    url = f"https://api.pagerduty.com/incidents?limit=999&team_ids[]={teamid}&time_zone=UTC&since={start}Z&until={end}Z"
    pageroutput = requests.get(
        url, headers={"authorization": f"Token token={apikey}"}
    ).json()
    output = []
    headers = ["Time(UTC)", "Description", "Status", "Notes"]
    output.append(f"|{'|'.join(headers)}|")
    output.append(re.sub("\|\-", "|:", re.sub("[^|]", "-", f"|{'|'.join(headers)}|")))
    for i in pageroutput["incidents"]:
        output.append(
            f"|{i['created_at']}|{i['title'].strip()}|{i['status']}|{fetch_note(i['id'], apikey)}|"
        )
        i_hour = arrow.get(i["created_at"]).floor("hour").format("YYYY-MM-DDTHH:mm:ss")
        incident_time[i_hour] = incident_time[i_hour] + 1
    if kwargs.get("html"):
        print(markdown.markdown("\n".join(output), extensions=["tables"]))
    else:
        print("\n".join(output))
    if kwargs.get("graph"):
        import plotly.graph_objects as go
        import pandas as pd

        df = pd.Series(incident_time).explode().reset_index(name="counter")
        fig = go.Figure([go.Scatter(x=df["index"], y=df["counter"])])
        fig.update_layout(
            xaxis_range=[
                arrow.get(kwargs.get("start")).datetime,
                arrow.get(kwargs.get("end")).datetime,
            ]
        )
        fig.show()


if __name__ == "__main__":
    main()
