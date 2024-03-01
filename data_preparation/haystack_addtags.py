#!/usr/bin/env python
# coding: utf-8

# In[1]:


import neo4j


# In[2]:


import pandas as pd


# In[3]:


import json


directory = 'path/to/wiki_data'  # Update this to your directory path


# In[5]:


with open("proto_wiki_data.json") as f:
    relevant = json.load(f)


import json



# In[7]:


from neo4j import GraphDatabase


# In[8]:


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


# In[10]:


import os


# In[11]:


files = [f for f in os.listdir(directory) if f.endswith('.txt')]


# In[12]:


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


# In[ ]:




