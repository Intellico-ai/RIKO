#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json



# This will hold all the JSON objects
all_data = []
count=0
with open("WikiMed.json", "r") as f:
    for line in f:
        # Try to parse each line as a JSON object
        try:
            data = json.loads(line)
            all_data.append(data)
        except json.JSONDecodeError:
            # Handle the case where a line is not valid JSON
            print("Found line that is not valid JSON:", line)
        count+=1
        if count==100000: break


# In[7]:


from bertopic import BERTopic


# In[4]:


import re


# In[5]:


def clean_string(input_string):
    # This pattern matches anything that is NOT a letter (a-z, A-Z) or punctuation
    pattern = r'[^a-zA-Z\.\,\!\?\:\;\- ]'
    cleaned_string = re.sub(pattern, '', input_string)
    return cleaned_string


# In[8]:


topic_model = BERTopic()



texts = []
for data in all_data:
    try:
     texts.append(clean_string(data["text"]))
    except:
        pass


# In[25]:



topics, probs = topic_model.fit_transform(texts)


# In[27]:


topic_info = topic_model.get_topic_info()



topic_info.to_csv("wiki_topics.csv", index=False)


# In[65]:


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


# In[62]:


with open("proto_wiki_data.json", "w") as f:
    json.dump(all_data, f)

