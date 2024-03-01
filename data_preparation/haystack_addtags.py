#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

from neo4j import GraphDatabase

import json
import os

directory = 'path/to/wiki_files'  # Update this to your directory path


with open("proto_wiki_data.json") as f:
    relevant = json.load(f)



driver = GraphDatabase.driver("bolt://"+"localhost"+":"+"7688", auth=("neo4j", "password"))


# In[36]:


def add_tags_node(tx, file_path, tags):
    
    query = """
        MATCH (d:Document {file_path : $file_path})
        MERGE (c:Tag { topic: $topic})
        MERGE (d)-[:TAG]->(c)
    """
    
    
    for tag in tags:
         tx.run(query, file_path = file_path, topic=tag)



files = [f for f in os.listdir(directory) if f.endswith('.txt')]



count=0
for i, ii in enumerate(relevant):
    try:
        text = ii["text"]
        title = ii["title"]
        unsafe_title = title.replace("_", "/").replace("_", ":")
        tags = [ii["topic"]]
       # key = files[i]
            
        with driver.session() as session:
            session.write_transaction(add_tags_node, directory+"/"+unsafe_title+".txt",  tags )
            
    except:
        pass


#building the index

query = "CREATE FULLTEXT INDEX documentContent FOR (n:Document) ON EACH [n.content]"
with driver.session() as session:
    session.run(query)



