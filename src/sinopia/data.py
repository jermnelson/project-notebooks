__author__ = "Jeremy Nelson"
__license__ = "Apache 2"

import pandas as pd

def commits_data_frame(**kwargs):
    """Takes JSON Github v4 commits payload and returns a Panda's
    data DataFrame

    Keyword arguments:
    commits -- list of commits
    """
    commits = kwargs.get('commits', [])
    additions, deletions, author, headline, committedDate, authorDate = {}, {}, {}, {}, {}, {}
    for row in commits:
        node = row['node']
        oid = node['oid']
        committedDate[oid] = pd.Timestamp(node['committedDate'])
        author[oid] = node['author']['user']['login']
        authorDate[oid] = pd.Timestamp(node['author']['date'])
        headline[oid] = node['messageHeadline']
        additions[oid] = node['additions']
        deletions[oid] = node['deletions']
    df = pd.DataFrame({
        'author': author,
        'headline': headline,
        'additions': additions,
        'deletions': deletions,
        'authorDate': authorDate,
        'committedDate': committedDate
    })
    df['elapsed'] = df['committedDate'] - df['authorDate']
    return df

def issues_data_frame(**kwargs):
    """Takes a JSON Github v4 issues payload and returns a Panda's
    data frame.

    Keyword arguments:
    issues -- list of issues
    """
    issues = kwargs.get('issues', [])
    closed, created, title, state, project, participants = {}, {}, {}, {}, {}, {}
    for row in issues:
        node = row['node']
        created[node['number']] = pd.Timestamp(node['createdAt'])
        if node.get('closedAt') is not None:
            closed[node['number']] = pd.Timestamp(node['closedAt'])
        title[node['number']] = node['title']
        state[node['number']] = node['state']
        # Add project
        if len(node["projectCards"]["edges"]) > 0:
            projects = []
            for project_row in node["projectCards"]["edges"]:
                projects.append(project_row['node']['project']['number'])
            project[node['number']] =  projects
        # Add participants
        agents = []
        for participant in node['participants']['edges']:
            agents.append(participant['node']['login'])
        participants[node['number']] = agents
    df = pd.DataFrame({
        'created': created,
        'closed': closed,
        'participants': participants,
        'project': project,
        'title': title,
        'state': state
    })
    df['elapsed'] = df['closed'] - df['created']
    return df
