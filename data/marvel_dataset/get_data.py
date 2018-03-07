import requests as rq
import json, re, os

def get_list_of_chars(cla):
    """Input 'heroes' or 'villains' and return list of characters."""
    # Format query
    endpoint = "https://en.wikipedia.org/w/api.php?"
    action = "action=query"
    _list = "list=categorymembers"
    _format = "format=json"
    cmtitle = "cmtitle=Category:Marvel_Comics_super%s" % cla
    cmlimit = "cmlimit=500"
    cmcontinue = ""

    characters = []
    while True:
        query_url = "&".join([endpoint, action, _list, cmtitle, _format, cmlimit, cmcontinue])
        data = rq.get(query_url, headers={'User-agent': 'ulfs bot'}).json()
        characters.extend([(c['title'], c['pageid']) for c in data['query']['categorymembers']])
        
        if 'continue' not in data:
            break
        
        cmcontinue = 'cmcontinue=' + data['continue']['cmcontinue']

    return characters

# Extract lists of characters
superheroes = get_list_of_chars('heroes')
supervillains = get_list_of_chars('villains')

# Download their page markup
for c in set(superheroes) | set(supervillains):
    
    # Get the faction of the character
    if c in superheroes and c in supervillains:
        folder = "ambiguous"
    elif c in superheroes:
        folder = "heroes"
    elif c in supervillains:
        folder = "villains"
    
    # Create folder  
    os.makedirs(folder, exist_ok=True)

    # Only download new pages
    if c[0] + ".txt" in os.listdir('%s' % folder):
        continue

    # Replace slash with dash (one character has a "/" in their name)
    if "/" in c[0]:
        c = (c[0].replace("/", "-"), c[1])
    
    # Get the data
    data = rq.get(
        "https://en.wikipedia.org/w/api.php?&prop=revisions&rvprop=content&action=query&pageids=%d&format=json" % c[1]
    ).json()
    
    # Get the markup
    markup = list(data['query']['pages'].values())[0]['revisions'][0]['*']
    
    # Save it
    with open("%s/%s.txt" % (folder, c[0]), 'w') as fp:
        fp.write(markup)
