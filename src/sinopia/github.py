__author__ = "Jeremy Nelson"
__license__ = "Apache 2"

import datetime
import os
import requests

GITHUB_URL = 'https://api.github.com/graphql'
ROOT_DIR = os.path.abspath(".").split('/Sinopia')[0]
ENV_PATH = os.path.join(ROOT_DIR, '.env')
with open(ENV_PATH) as fo:
    token = fo.read()[:-1]
    GITHUB_HEADERS = {'Authorization': f"token {token}"}

def all_issues(**kwargs):
    """Queries Github and retrieves all state issues in a Github repository


    Keyword arguments:
    repo -- The name of the LD4P repository (defaults sinopia_editor)
    state -- The state of the issues, (defaults OPEN)
    """
    issues = []
    repo = repo=kwargs.get('repo', 'sinopia_editor')
    closed_issues = issues_query(repo=repo,
                                 state="CLOSED")
    issues.append(closed_issues)
    hasNextPage = closed_issues['data']['repository']['issues']['pageInfo']['hasNextPage']
    while hasNextPage:
        closed_issues = issues_query(repo=repo,
            state="CLOSED",
            after=closed_issues['data']['repository']['issues']['pageInfo']['endCursor'])
        issues.append(closed_issues)
        hasNextPage = closed_issues['data']['repository']['issues']['pageInfo']['hasNextPage']
    return issues

def issues_query(**kwargs):
    """Queries with graph QL for issues and returns json

    Keyword arguments:
    repo -- The name of the LD4P repository (defaults sinopia_editor)
    state -- The state of the issues, (defaults OPEN)
    first -- number of items from the first (defaults 100)
    after -- End cursor
    """
    after = kwargs.get('after', '')
    if len(after) > 0:
        after = """, after: "{after}" """.format(after=after)
    query = {
        'query': """{{
            repository(owner:"LD4P", name:"{repo}") {{
              issues(first:{first} {after}) {{
                pageInfo {{
                    startCursor
                    hasNextPage
                    endCursor
                }}
                edges {{
                  node {{
                    title
                    url
                    number
                    createdAt
                    closedAt
                    projectCards(first:5) {{
                      edges {{
                          node {{
                              project {{
                                      name
                                      number
                              }}
                              state
                          }}
                      }}
                    }}
                    participants(first:10) {{
                        edges {{
                            node {{
                                login
                            }}
                        }}
                    }}
                    state
                  }}
                }}
              }}
           }}
        }}
    """.format(state=kwargs.get('state', 'OPEN'),
               first=kwargs.get('first', 100),
               repo=kwargs.get('repo', 'sinopia_editor'),
               after=after)
    }
    result = requests.post(url=GITHUB_URL, json=query, headers=GITHUB_HEADERS)
    payload = result.json()
    if "errors" in payload.keys():
        print(payload)
    return payload
