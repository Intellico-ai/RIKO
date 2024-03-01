

import spacy 


from haystack import component
from typing import List

from haystack.dataclasses.document import Document




@component
class AnnotatortoRetriever:
  """
  A component generating personal welcome message and making it upper case
  """
  
  
  
  @component.output_types(entities= str)
  def run(self, documents: List[Document]):
    
    annotations = []
    for doc in documents:
      ents = doc.meta["named_entities"]
      for ent in ents:
        start = ent.start
        end   = ent.end
        annotations.append(doc.content[start:end])
      
    entities = annotations[0]
    
    for ii in annotations[1:]:
       entities = entities+" AND "+ii
      
    return {"entities": entities}
      
    
@component
class Nouns_Exctractor():
  def __init__(self):
    """
    A component generating personal welcome message and making it upper case
    """
  
    self.nlp = spacy.load("en_core_web_sm")
  
  @component.output_types(entities= str)
  def run(self, documents: List[Document]):
    
    
    


    annotations = []
   
    for doc in documents:
      
      doc_loaded = self.nlp(doc.content)
      
      for token in doc_loaded:
        if (token.pos_ in ["PROPN", "NOUN"]):
          annotations.append(token.text)
        
      
      
    entities = annotations[0]
    
    for ii in annotations[1:]:
       entities = entities+" AND "+ii
      
    return {"entities": entities}
      
    
