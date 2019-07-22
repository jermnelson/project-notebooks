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

def issues_query(**kwargs):
    """Queries with graph QL for issues and returns json

    Keyword arguments:
    repo -- The name of the LD4P repository (defaults sinopia_editor)
    state -- The state of the issues, (defaults OPEN)
    first -- number of items from the first (defaults 100)
    """
    query = {
        'query': """{{
            repository(owner:"LD4P", name:"{repo}") {{
              issues(states:{state}, first:{first}) {{
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
                  }}
                }}
              }}
           }}
        }}
    """.format(state=kwargs.get('state', 'OPEN'),
               first=kwargs.get('first', 100),
               repo=kwargs.get('repo', 'sinopia_editor'))
    }
    result = requests.post(url=GITHUB_URL, json=query, headers=GITHUB_HEADERS)
    return result.json()
