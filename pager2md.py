#!/usr/bin/env python

import re
import requests
import arrow
import click


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
@click.option("--teamid", required=True)
@click.option("--start", required=True, help="The date format in 2021-01-28T03:30:21")
@click.option("--duration", required=True, help="Duration for this query in hours")
@click.option("--apikey", required=True, help="Pagerduty API key")
def main(**kwargs):
    start = arrow.get(kwargs.get("start"))
    end = start.shift(hours=+int(kwargs.get("duration")))
    if arrow.utcnow() < end:
        end = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ss")
    start = arrow.get(kwargs.get("start")).format("YYYY-MM-DDTHH:mm:ss")
    teamid = kwargs.get("teamid")
    apikey = kwargs.get("apikey")
    url = f"https://api.pagerduty.com/incidents?total=false&team_ids[]={teamid}&time_zone=UTC&since={start}Z&until={end}Z"
    pageroutput = requests.get(
        url, headers={"authorization": f"Token token={apikey}"}
    ).json()
    output = []
    headers = ["Time(UTC)", "Description", "Status", "Notes"]
    output.append(f"|{'|'.join(headers)}|")
    output.append(re.sub("[^|]", "-", f"|{'|'.join(headers)}|"))
    for i in pageroutput["incidents"]:
        output.append(
            f"|{i['created_at']}|{i['title'].strip()}|{i['status']}|{fetch_note(i['id'], apikey)}|"
        )
    print("\n".join(output))


if __name__ == "__main__":
    main()
