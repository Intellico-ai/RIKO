#!/usr/bin/env python
# coding: utf-8

# In[1]:


import neo4j


# In[2]:


import pandas as pd


# In[3]:


import json


# In[4]:


directory = 'path/to/wiki_data'  # Update this to your directory path


# In[5]:


with open("proto_wiki_data.json") as f:
    relevant = json.load(f)


# In[6]:


relevant[-1]



# In[7]:


import os

def find_files_containing_string(directory, input_string):
    # Replace spaces in the input string if needed
    search_string = input_string.replace(" ", "")
    search_string = search_string.replace("\n", "")
    search_string = search_string.replace("*", "")
    search_string = search_string.replace("#", "")
    print(search_string)
    
    # List all .txt files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    # List to hold files containing the input string
    files_containing_string = []
    
    # Loop through files and search for the input string
    for file in files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().replace(" ", "")
            content = content.replace("\n", "")
            content = content.replace("*", "")
            content = content.replace("#", "")
           # print(content)
            if search_string in content:
                files_containing_string.append(file)
      #  break
    return files_containing_string

# Example usage



# In[8]:


doc_quest = []


# In[ ]:


for iter, ii in enumerate(relevant):
    try:
        file = find_files_containing_string(directory, ii["document"][80:120])[0]
        doc_quest.append({file: ii["questions"]})
    except:
        print( iter)


# In[5]:


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




