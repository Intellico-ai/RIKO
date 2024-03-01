from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import HuggingFaceTGIGenerator, OpenAIGenerator
from haystack.utils import Secret


from neo4j_haystack import Neo4jClientConfig, Neo4jDynamicDocumentRetriever



from haystack.components.extractors import NamedEntityExtractor
from haystack.components.converters import TextFileToDocument

from haystack.dataclasses.document import Document



import gradio as gr




from haystack import component
from typing import List

import spacy 


# In[4]:


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
      
    


# In[5]:


client_config = Neo4jClientConfig(
    url="bolt://localhost:7688",
    username="neo4j",
    password="password",
    database="neo4j",
)

cypher_query = """
            CALL db.index.fulltext.queryNodes("documentContent", $entities) YIELD node as doc, score
            MATCH (doc) 
            RETURN doc{.*, score}, score
            ORDER BY score DESC LIMIT $top_k
        """
        
        
prompt_template = """
Given the following documents, answer the question.\nDocuments:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}

\Question: {{question}}
\nAnswer:
"""




rag_pipeline = Pipeline()


# rag_pipeline.add_component(
#     "entity_extraction",
#    NamedEntityExtractor(backend="spacy", model="en_core_web_trf") #(backend="hugging_face",  model="dslim/bert-base-NER"),
# )

rag_pipeline.add_component("extracter_to_retriever", Nouns_Exctractor())
rag_pipeline.add_component(
    "retriever",
    Neo4jDynamicDocumentRetriever(
        client_config=client_config,
        runtime_parameters=["entities"],
        doc_node_name="doc",
        verify_connectivity=True,
    ),
)
rag_pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipeline.add_component(
    "llm",
    OpenAIGenerator(),
)
rag_pipeline.add_component("answer_builder", AnswerBuilder())






# rag_pipeline.connect("entity_extraction.documents", "extracter_to_retriever.documents")

rag_pipeline.connect("extracter_to_retriever.entities", "retriever.entities")
rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("llm.meta", "answer_builder.meta")
rag_pipeline.connect("retriever", "answer_builder.documents")






def search(query, history):
    question = query
    documento = Document(content=question)
    result = rag_pipeline.run(
    {
        "extracter_to_retriever": {"documents": [documento]},
        "retriever": {
            "query": cypher_query,
            "parameters": { "top_k": 3}, 
        },
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question},
    }
)
    answer: GeneratedAnswer = result["answer_builder"]["answers"][0]
    formatted_results = answer.data
    
    documents = answer.documents
    
    docs = []
    
    
    
    documents_str = ""
    for doc in documents:
        path = doc.meta["file_path"]
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        documents_str += f"Document: {source}\n\n"
    
    # Combine the answer and the documents into a single string
    combined_result = [f"Answer:\n{formatted_results}", f"Related Documents:{documents_str}"]
    
    return combined_result

# Update the Gradio interface setup to match the new API
iface = gr.Interface(
    fn=search, 
    inputs=gr.Textbox(label="Query"), 
    outputs=[gr.Textbox(label="Result"),  gr.Textbox(label="Related Documents")]
)

iface.launch()

