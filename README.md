# TwitterMapper
## How to use:
Download tweets here: https://www.vicinitas.io/free-tools/download-user-tweets 
MAKE SURE TO INCLUDE THE @ IN THE FILE NAME (I don't error check lol)

Create a "Data" directory inside this repository, move all tweets into it

pip install matplotlib, openpyxl, networkx

run ```python excelparser.py```

To make index.html display your graph, add the following to the generated "graph.json": at the beginning, add "data ='" and at the end, add "'"

To include tweets, add the following to the generated "tweets.json": at the beginning, add "tweet_data = '" and at the end, add "'"