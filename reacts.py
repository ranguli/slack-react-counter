from datetime import datetime, date
import requests
import json
from decouple import config

import emoji

SLACK_API_TOKEN = config("SLACK_API_TOKEN")


def get_channels():

    channels = []

    url_endpoint = "https://slack.com/api/conversations.list"
    parameters = {"token": SLACK_API_TOKEN, "limit": 1000}

    raw_response = requests.get(url_endpoint, params=parameters)
    response = json.loads(raw_response.text)
    response = response.get("channels")

    for channel in response:
        # The API returns public channels by default but we'll double check:
        if not channel.get("is_private"):
            channels.append(channel.get("id"))

    return channels


def main():
    reaction_counter = {}
    message_count = 0
    reacted_message_count = 0

    channels = get_channels()
    for channel in channels:

        print("Working on channel " + channel)

        # How far back do we want to go
        old = datetime(2019, 1, 1).timestamp()

        url_endpoint = "https://slack.com/api/channels.history"
        parameters = {
            "token": SLACK_API_TOKEN,
            "channel": channel,
            "count": 1000,
            "oldest": old,
        }

        raw_response = requests.get(url_endpoint, params=parameters)
        response = json.loads(raw_response.text)

        messages = response.get("messages")

        for message in messages:
            message_count += 1
            reacts = message.get("reactions")

            if reacts:
                reacted_message_count += 1
                if len(reacts) > 1:
                    for react in reacts:
                        colonified = "".join((":", reacts[0].get("name"), ":"))

                        if colonified not in reaction_counter:
                            reaction_counter[colonified] = 1
                        else:
                            reaction_counter[colonified] += reacts[0].get("count")
                else:
                    colonified = "".join((":", reacts[0].get("name"), ":"))
                    if colonified not in reaction_counter:
                        reaction_counter[colonified] = 1
                    else:
                        reaction_counter[colonified] += reacts[0].get("count")

    reaction_counter = {
        k: v for k, v in sorted(reaction_counter.items(), key=lambda item: item[1])
    }

    for k, v in reaction_counter.items():
        print(emoji.emojize(k, use_aliases=True) + "\t" + str(v))

    print(
        str(reacted_message_count)
        + "/"
        + str(message_count)
        + " had reacts ("
        + str(reacted_message_count / message_count * 100)
        + "%)"
    )


main()
