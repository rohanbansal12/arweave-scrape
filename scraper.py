from cProfile import run
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import time
import random
from pathlib import Path
import requests
import argparse


transport = AIOHTTPTransport(url="https://arweave.net/graphql", ssl_close_timeout=50, timeout=50)
client = Client(transport=transport, fetch_schema_from_transport=True)

proxies_list = []


def run_snapshot_query(q, retries=0):
    proxies = {"http": random.choice(proxies_list)} if proxies_list else None

    if retries > 10:
        print("Failed to run query")
        return -1
    try:
        response = requests.post("https://arweave.dev/graphql", "", json={"query": q}, proxies=proxies)
        if response.status_code == 200:
            return json.loads(response.text)["data"]
        else:
            time.sleep(0.5)
            return run_snapshot_query(q, retries=retries + 1)
    except:
        time.sleep(0.5)
        return run_snapshot_query(q, retries=retries + 1)


def get_transactions(cursor, retries=0):
    if retries == 10:
        return -1
    try:
        return client.execute(query, variable_values={"cursor": cursor})["transactions"]["edges"]
    except Exception as e:
        return get_transactions(cursor, retries + 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cursor", type=str, default="last_cursor.txt")
    parser.add_argument("--results", type=str, default="sample_aw.json")
    parser.add_argument("--query", type=str, default="query.txt")
    parser.add_argument("--proxies", type=str, default=None)
    args = parser.parse_args()

    cursor_path = Path(args.cursor)
    results_path = Path(args.results)
    query_path = Path(args.query)

    if args.proxies:
        with open(args.proxies, "r") as f:
            proxies_list = f.readlines()

    with open(query_path, "r") as f:
        raw_query = f.read()

    if cursor_path.exists():
        with open(cursor_path, "r") as f:
            last_cursor = f.readlines()[0].strip().replace("\n", "")
        if results_path.exists():
            with open(results_path, "r") as f:
                all_entries = json.load(f)
        else:
            all_entries = []
    else:
        all_entries = []
        last_cursor = ""

    print("Starting from cursor: ", last_cursor)
    print("Total loaded entries: ", len(all_entries))

    query = gql(raw_query)
    new_query = raw_query.replace("$cursor", f'"{last_cursor}"')
    result = run_snapshot_query(new_query)["transactions"]["edges"]

    while result:
        all_entries.extend(result)
        if len(all_entries) % 500 == 0:
            print(f"{len(all_entries)} entries")
        if len(all_entries) % 100000 == 0:
            with open(results_path, "w") as f:
                json.dump(all_entries, f)
            with open(cursor_path, "w") as f:
                f.write(last_cursor)
        last_cursor = result[-1]["cursor"]
        new_query = raw_query.replace("$cursor", f'"{last_cursor}"')
        result = run_snapshot_query(new_query)
        if result == -1:
            with open(results_path, "w") as f:
                json.dump(all_entries, f)
            with open(cursor_path, "w") as f:
                f.write(last_cursor)
            time.sleep(5)
            exit(1)
        result = result["transactions"]["edges"]

    print(f"Final: {len(all_entries)} entries")
    with open("sample_aw.json", "w") as f:
        json.dump(all_entries, f)
