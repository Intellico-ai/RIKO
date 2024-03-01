#!/usr/bin/env python
# coding: utf-8

# In[1]:


import logging
import os
import zipfile
from io import BytesIO
from pathlib import Path
import json

import requests
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter

from neo4j_haystack import Neo4jDocumentStore

logger = logging.getLogger(__name__)


# In[2]:


# In[3]:


# Let's first get some files that we want to use
docs_dir = "/path/to/wiki_data"
# fetch_archive_from_http(
#     url="https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/wiki_gameofthrones_txt6.zip",
#     output_dir=docs_dir,
# )


all_data= []
count=0
with open("WikiMed.json", "r") as f:
    for line in f:
        # Try to parse each line as a JSON object
        #try:
        data = json.loads(line)
        data[ "topic"]= topic_info[topic_info["Topic"]==topics[count]]["Name"].iloc[-1]
        all_data.append(data)

        safe_title = data["title"].replace("/", "_").replace(":", "_")

        with open(f"wiki_data/{safe_title}.txt", "w") as f:
            f.write(data["text"])
        count+=1
        if count==100000: break

# In[4]:


document_store = Neo4jDocumentStore(
    url="bolt://localhost:7688",
    username="neo4j",
    password="password",
    database="neo4j",
    embedding_dim=384,
    similarity="cosine",
    recreate_index=True,
)


# In[5]:


# Create components and an indexing pipeline that converts txt to documents, cleans and splits them, and
# indexes them for dense retrieval.
p = Pipeline()
p.add_component("text_file_converter", TextFileToDocument())
p.add_component("cleaner", DocumentCleaner())
p.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=250, split_overlap=30))
p.add_component("embedder", SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", device="cuda"))
p.add_component("writer", DocumentWriter(document_store=document_store))

p.connect("text_file_converter.documents", "cleaner.documents")
p.connect("cleaner.documents", "splitter.documents")
p.connect("splitter.documents", "embedder.documents")
p.connect("embedder.documents", "writer.documents")


# In[6]:


# Take the docs data directory as input and run the pipeline
file_paths = [docs_dir / Path(name) for name in os.listdir(docs_dir)]
result = p.run({"text_file_converter": {"sources": file_paths}})

