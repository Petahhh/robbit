import urllib.request
import urllib.parse
import sys
import json

DEBUG = False

def print_debug(what, message):
    if DEBUG:
        print("<debug = {}> -> {}".format(what, message))

def send_message(slack_message):
    print_debug("slack_message", slack_message)

    slack_url = "https://slack.com/api/chat.postMessage"
    slack_data = {
        "token": slack_token,
        "channel": slack_channel,
        "text": slack_message,
        "username": "robbit",
        "icon_emoji": ":rabbit:",
    }

    response = urllib.request.urlopen(slack_url, data=urllib.parse.urlencode(slack_data).encode('utf-8'))
    print_debug("response_status", response.status)
    print_debug("response_body", response.read().decode('utf-8'))


def get_in_progress_retro_items():
    headers = {
        'authorization': postfacto_token,
        'content-type': 'application/json',
        'Accept': "*/*",
    }
    url = 'https://retros-iad-api.cfapps.io/retros/' + retro_id
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)


    retro = json.loads(response.read().decode('utf-8'))["retro"]
    in_progress_action_items = [item for item in retro["action_items"] if not item["done"]]
    sorted_in_progress_action_items = sorted(in_progress_action_items, key=lambda x: x["created_at"])

    descriptions = [item["description"] for item in sorted_in_progress_action_items]

    return descriptions

def build_slack_map_dict(initials_slack_map):

    slack_map_dict = {}
    users_array = initials_slack_map.split(",")
    for user in users_array:
        user_and_handle = user.split(":")
        slack_name_with_link="<@" + user_and_handle[2] + "|" + user_and_handle[1] + ">"
        if user_and_handle[1] == "cloud-cache-eng":
            slack_name_with_link="<!subteam^" + user_and_handle[2] + "|" + user_and_handle[1] + ">"
        slack_map_dict[user_and_handle[0]] = slack_name_with_link

    return slack_map_dict

def add_slack_handles(retro_items, slack_map_dict):
    retro_items_with_slack_handles = []
    for retro_item in retro_items:
        retro_items_with_slack_handles.append(retro_item)
        for (initial, slack_handle) in slack_map_dict.items():
            if "[" + initial + "]" in retro_item:
                del retro_items_with_slack_handles[-1]
                retro_items_with_slack_handles.append(slack_handle + " " + retro_item)
                break
    return retro_items_with_slack_handles

if __name__ == "__main__":
    print_debug("hello_message", "Hello There!")

    script_path, postfacto_token, retro_id, slack_token, slack_channel, initials_slack_map = sys.argv

    print_debug("postfacto_token", postfacto_token)
    print_debug("retro_id", retro_id)
    print_debug("slack_token", slack_token)
    print_debug("slack_channel", slack_channel)
    print_debug("initials_slack_map", initials_slack_map)

    retro_items = get_in_progress_retro_items()
    retro_items_with_slack_handles = add_slack_handles(retro_items, build_slack_map_dict(initials_slack_map))

    good_morning_message = ["*Goooooooooooooooood morning Gems! :gem:",]
    retro_items_message = ["(%s) Retro items:" % len(retro_items_with_slack_handles)] + retro_items_with_slack_handles
    retro_items_message = good_morning_message + retro_items_message

    postfacto_reminder_message=["All done? Check off your tasks at: https://retros.cfapps.io/retros/" + retro_id]
    standup_vote_message=['</poll> <!here> "*Did you enjoy the standup this morning?*" "yay" "meh" "nay"']

    send_message("\n".join(retro_items_message))
    send_message("\n".join(postfacto_reminder_message))
