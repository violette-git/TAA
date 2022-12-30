import requests
import datetime
import json
import time
import re
import os
from dotenv import load_dotenv

load_dotenv()  

repos_url = "https://api.github.com/orgs/{org}/repos"
users_url = "https://api.github.com/repos/{org}/{repo}/collaborators"
activity_url = "https://api.github.com/repos/{org}/{repo}/commits?author={user}"

KEY = os.getenv('API_KEY')

headers = {"Authorization": f"Token {KEY}"}

def reset_data():
    with open("data.json", "w") as f:
        json.dump({}, f)

def get_repos(org):
    params = {"sort": "created", "direction": "desc"}
    response = requests.get(repos_url.format(org=org), params=params, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_users(org, repo):
    response = requests.get(users_url.format(org=org, repo=repo), headers=headers)
    if response.status_code == 200:
        return response.json()
    # else:
    #     return []

def get_activity(org, repo, user):
    response = requests.get(activity_url.format(org=org, repo=repo, user=user), headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def is_valid_iso_format(string):
    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?Z"
    return bool(re.match(pattern, string))

def check_commit(activity, date):
    for commit in activity:
        commit_time_string = commit["commit"]["committer"]["date"]
        commit_time_format = "%Y-%m-%dT%H:%M:%SZ"
        commit_time = datetime.datetime.strptime(commit_time_string, commit_time_format)
        if commit_time.date() == date.date():
            return True
    return False

def main():
    now = datetime.datetime.now()
    if now.hour == 0:
        reset_data()
    org = input("Enter the name of the organization: ")
    repos = get_repos(org)
    if repos:
        print("Available repositories:")
        for i, repo in enumerate(repos):
            print(f"{i+1}. {repo['name']}")
        repo_index = int(input("Enter the number of the repository you want to select: ")) - 1
        repo = repos[repo_index]["name"]
        users = get_users(org, repo)
        if users:
            with open("data.json", "r") as f:
                data = json.load(f)
            repo_data = {}
            date_string = input("Enter the date you want to check (YYYY-MM-DD): ")
            for user in users:
                activity = get_activity(org, repo, user["login"])
                commit_activity = []
                date_format = "%Y-%m-%d"
                date = datetime.datetime.strptime(date_string, date_format)
                print(date)
                made_commit = check_commit(activity, date)
                print(made_commit)
                if made_commit:
                    commit_activity.append({"date": date.isoformat(), "commit": "yes"})
                else:
                    commit_activity.append({"date": date.isoformat(), "commit": "no"})
                repo_data[user["login"]] = commit_activity
            data[repo] = repo_data
            with open("data.json", "w") as f:
                json.dump(data, f)

# Run the main function 3 times a day, 8 hours apart ??

main()
