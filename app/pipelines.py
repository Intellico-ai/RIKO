

from neo4j_haystack import Neo4jDynamicDocumentRetriever, Neo4jClientConfig
from haystack import Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import  OpenAIGenerator

from .components import Nouns_Exctractor
from .prompts import prompt_template


client_config = Neo4jClientConfig(
    url="bolt://localhost:7688",
    username="neo4j",
    password="password",
    database="neo4j",
)



rag_pipeline = Pipeline()




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

