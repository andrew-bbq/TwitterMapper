import openpyxl
from pathlib import Path
from os import listdir
from os.path import isfile, join
import re
import networkx as nx
import matplotlib.pyplot as plt
import math
import json

onlyfiles = [f for f in listdir("Data") if isfile(join("Data", f))]
usernames = []
references = {}
totalinteractions = {}
tweet_list = {}
# set up data structures
for filename in onlyfiles:
    username = filename.split("_user")[0]
    usernames.append(username)
    references[username] = {}
    totalinteractions[username] = 0

# go through all files, add to total count when tracked user is found
# we'll generate a graph from this later
for filename in onlyfiles:
    username = filename.split("_user")[0]
    tweet_list[username] = {}
    path = "./Data/"+filename
    wb_obj = openpyxl.load_workbook(path)
    sheet_obj = wb_obj.active
    for i, row in enumerate(sheet_obj.iter_rows(values_only=True)):
        try:
            users = re.findall("@[A-Za-z0-9_-]*", row[1])
            for user in users:
                if user in usernames and user != username:
                    totalinteractions[username] = totalinteractions[username] + 1
                    if user not in tweet_list[username]:
                        tweet_list[username][user] = []
                    tweet_list[username][user].append("http://twitter.com/"+row[3]+"/status/"+row[0])
                    if user in references[username]:
                        references[username][user] = references[username][user]+1
                    else:
                        references[username][user] = 1
        except:
            continue
        
# bootleg jaccard value calculations
jaccard_values = {}
for user in usernames:
    jaccard_values[user] = {}
for user in usernames:
    for ref_user in references[user]:
        ext_count = 0
        if user in references[ref_user]:
            ext_count = references[ref_user][user]
        union_count = references[user][ref_user] + ext_count
        total_count = totalinteractions[user] + totalinteractions[ref_user]
        jac_val = (union_count / total_count) * 100
        if jac_val >= 1:
            jaccard_values[user][ref_user] = jac_val
            jaccard_values[ref_user][user] = jac_val

def calc_modularity_gain(sigma_tot, sigma_in, i_sum, i_sum_in_c, m):
    part_one = ((sigma_in + i_sum_in_c) / (2*m)) - math.pow(((sigma_tot + i_sum) / (2*m)),2)
    part_two = ((sigma_in)/(2*m)) - math.pow(((sigma_tot) / (2*m)),2) - math.pow(((i_sum)/(2*m)), 2)
    return (part_one - part_two)

# find communities: https://arxiv.org/pdf/0803.0476.pdf
# begin by summing all edges - necessary for modularity calculation
m = 0
communities = []
for user in usernames:
    jac_sum = 0
    for user2 in usernames:
        if user2 in jaccard_values[user]:
            m = m + jaccard_values[user][user2]
            jac_sum += jaccard_values[user][user2]
        elif user in jaccard_values[user2]:
            m = m + jaccard_values[user2][user]
            jac_sum += jaccard_values[user2][user]
    communities.append({"users": [user], "out_edges": jaccard_values[user], "in_edges": {}, "sum_in": 0, "sum_out": jac_sum})
print(m)
print(len(usernames))
moved = 1
passes = 0
while moved > 0 and passes < 75:
    passes = passes + 1
    moved = 0
    if len(communities) < 2:
        break
    for username in usernames:
        adjacent = jaccard_values[username]
        highestNeighbor = None
        highestModGain = 0
        for neighbor in adjacent:
            same_community = False
            community = None
            for c in communities:
                if neighbor in c["users"]:
                    if user not in c["users"]:
                        community = c
                    else:
                        same_community = True
            if not same_community and community is not None:
                ki = 0
                kiin = 0
                for user2 in adjacent:
                    if user2 in community["users"]:
                        kiin += adjacent[user2]
                    ki += adjacent[user2]
                mod_gain = calc_modularity_gain(community["sum_out"], community["sum_in"], ki, kiin, m)
                if mod_gain > highestModGain:
                    highestModGain = mod_gain
                    # arbitrary person in community, used for finding community later
                    highestNeighbor = community["users"][0]
        if highestNeighbor is not None:
            # username wants to join highestNeighbor, so we need to update the community list
            # find community with username in it, remove it, do calculations
            for i in range(len(communities)):
                if username in communities[i]["users"]:
                    communities[i]["users"].remove(username)
                    if len(communities[i]["users"]) == 0:
                        communities.pop(i)
                        break
                    else:
                        # UPDATE COMMUNITY CALCULATIONS HERE!!!!!
                        sum_tot = 0
                        sum_in = 0
                        for comm_user in communities[i]["users"]:
                            out_edges = jaccard_values[comm_user]
                            # in edges will be added twice so we'll divide by two for them
                            for edge in out_edges:
                                if edge in communities[i]["users"]:
                                    sum_in += (out_edges[edge] / 2)
                                sum_tot += out_edges[edge]
                            communities[i]["sum_out"] = sum_tot
                            communities[i]["sum_in"] = sum_in
            # add user to new community, update calculations
            for i in range(len(communities)):
                if highestNeighbor in communities[i]["users"]:
                    communities[i]["users"].append(username)
                    # UPDATE COMMUNITY CALCULATIONS HERE!!!!!
                    sum_tot = 0
                    sum_in = 0
                    for comm_user in communities[i]["users"]:
                        out_edges = jaccard_values[comm_user]
                        # in edges will be added twice so we'll divide by two for them
                        for edge in out_edges:
                            if edge in communities[i]["users"]:
                                sum_in += (out_edges[edge] / 2)
                            sum_tot += out_edges[edge]
                        communities[i]["sum_out"] = sum_tot
                        communities[i]["sum_in"] = sum_in
            moved = 1


for commune in communities:
    print(commune["users"])

# MAKE GRAPH AND DISPLAY
G = nx.Graph()
# could do this in previous for loop, doing it here for clarity
for user in jaccard_values:
    for ref_user in jaccard_values[user]:
        G.add_edge(user, ref_user, weight=jaccard_values[user][ref_user])

#for user in jaccard_values:
    #print(user)
    #print(jaccard_values[user])
    #print("\n")
pos = nx.spring_layout(G)
#print(pos)
nx.draw(G, pos=pos)
label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
nx.draw_networkx_labels(G, pos, font_size=8, bbox=label_options)
plt.show()

# colors for nodes- add more if you have more groups
colors = ["#4a87e8", "#e33d59", "#3ac959", "#FF00FF"]

# convert our graph to json for sigma.js
sigma_json = {}
counter = 0
visited = []
sigma_json["nodes"] = []
sigma_json["edges"] = []
for username in usernames:
    comm_number = 0
    comm_counter = 0
    for community in communities:
        if username in community["users"]:
            comm_number = comm_counter
        else:
            comm_counter += 1
    user_node = {}
    user_node["id"] = username
    user_node["label"] = username
    user_node["x"] = pos[username][0] * 4
    user_node["y"] = pos[username][1] * 4
    # will replace size with follower count later
    user_node["size"] = 3
    user_node["color"] = colors[comm_number]
    sigma_json["nodes"].append(user_node)
    for user2 in jaccard_values[username]:
        if user2 not in visited:
            user_edge = {}
            user_edge["id"] = "e" + str(counter)
            counter += 1
            user_edge["source"] = username
            user_edge["target"] = user2
            user_edge["size"] = jaccard_values[username][user2]
            sigma_json["edges"].append(user_edge)
    visited.append(username)

with open("graph.json", "w") as outfile:
    json.dump(sigma_json, outfile)

# throw our tweet map into a json too
with open("tweets.json", "w") as outfile:
    json.dump(tweet_list, outfile)