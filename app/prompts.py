






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
