from haystack import GeneratedAnswer

from neo4j_haystack import Neo4jClientConfig, Neo4jDynamicDocumentRetriever

from haystack.dataclasses.document import Document

import gradio as gr

from .prompts import  cypher_query
from .pipelines import rag_pipeline




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

