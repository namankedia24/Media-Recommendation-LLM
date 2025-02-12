import pysqlite3
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import time
from llama_index.core import QueryBundle
from llama_index.core.schema import TextNode
import os
import re
from openai import OpenAI
from llama_index.core.schema import TextNode
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

from config import VECTOR_STORE_DIR, EMBED_MODEL_NAME, LLM_MODEL_NAME


# import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
RETRIEVER_SIMILARITY_TOP_K: int = 5
RERANKER_CHOICE_BATCH_SIZE: int = 3

RERANKER_TOP_N: int = 1

# TODO: implement RAG pipline with metadata filtering and reranking.
# When initializing different object in the constructor, please make
# the objects protected, which is achieved by underscoring the beginning
# of the object, as in the example with the embedding model:
# self._embed_model = ...

# We suggest sticking to the provided template for we believe it to be
# the simplest implementation way. Please, provide explanation if you
# find it necessary to change template.


def calculate_time(func):
    
    def inner1(*args, **kwargs):

        # storing time before function execution
        begin = time.time()
        
        val = func(*args, **kwargs)

        # storing time after function execution
        end = time.time()
        print("Total time taken in : ", func.__name__, end - begin)
        return val

    return inner1

class RAGSystem:
    def __init__(self):
        # Initialize embedding model given EMBED_MODEL_NAME.

        self._embed_model = SentenceTransformer(EMBED_MODEL_NAME)
        # print("Embedding model loaded.")
    
        # Initialize a vector database from the existing collection
        # in VECTOR_STORE_DIR and a corresponding vector store index.
        # We recommend ChromaDB. Embedding model should be the same
        # as for storing the nodes.
        self.client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        collection_name = "final"
        # print("Loading collection...")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        # print("Loading collection...")

        # Initialize LLM given LLM_MODEL_NAME.
        # Tip: for the pipeline to work correctly, it is likely
        # you will need to create a tokenizer for the model.
        # We suggest looking into AutoTokenizer.
        
        togetherai_api_key = 'dd7aaa683f7a978000e2f6b9bb6df2a3ab1d7ecb7dc0aa248c989c1118a0c463'
        self.client_together = OpenAI(api_key=togetherai_api_key,
                base_url='https://api.together.xyz')
        # self.client_together = Together(api_key=togetherai_api_key)

        # Initialize reranker. We suggest LLM-based reranker with
        # RERANKER_CHOICE_BATCH_SIZE nodes to consider from the retriever and
        # RERANKER_TOP_N documents to return.
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        # print("Loading collection...")
    
    def searchmedia(self, query: str, searchoptions: list, year: str, referencemedia: str) -> tuple[str, TextNode]:
        """
        Given a questy, a ticker and a year, should return a response
        to the provided query for the given company in the given year and
        the most relevant node.
        """

        query_embedding = self._embed_model.encode(query).tolist()

        metadata_filter = {
            "$and": [
                {"ticker": {"$eq": referencemedia}},
                {"year": {"$eq": year}}
                ]
        }           

        # Initialize retriever from the vector store index
        # with the filters above and RETRIEVER_SIMILARITY_TOP_K.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=RETRIEVER_SIMILARITY_TOP_K,
            where=metadata_filter,
            include=["metadatas", "documents", "distances"]
        )
        
        # Retrieve the nodes for the provided query.
        retrieved_nodes = [
            TextNode(text=document, metadata=results["metadatas"][0][i])
            for i, document in enumerate(results["documents"][0])
        ]

        # print("Retrieved nodes:" + str(retrieved_nodes))
        # print(results['metadatas'][0])
        # Apply the reranker to the retrieved nodes and get
        # the best one.
        reranked_nodes = self.rerank(query, retrieved_nodes[:RERANKER_CHOICE_BATCH_SIZE])
        selected_node = reranked_nodes[0] if reranked_nodes else None
        print("Best retrieved node:" + str(selected_node.text) if selected_node else "No relevant context found.")

        # Merge the reranked nodes with the query and give it
        # to the LLM to get the response.
        # TODO
        llm_input_text = f"""
            Example 1:

            Reference Media: Inception (2010)
            Question: What are similar movies that have Leonardo DiCaprio in them?
            
            Response:

            1.Interstellar (2014) – 
            Directed by Christopher Nolan, 
            starring Leonardo DiCaprio 
            (originally rumored but not cast).

            2.Shutter Island (2010) – 
            Psychological thriller starring Leonardo DiCaprio.
            3.The Prestige (2006) – 
            Nolan’s film with a similar mind-bending narrative style.
            -------------------------------------------------------------------------------------------------------------------------
           
             Based on the reference media "Gossip Girl", here are some similar recommendations:

            Movies:

            1.The Devil Wears Prada (2006) – 
            A fashionable and dramatic film exploring the lives of Manhattan's elite.
            2.Easy A (2010) – 
            A teen comedy-drama that navigates high school social hierarchies and scandals.
            Books:

            1.The A-List series by Zoey Dean – A series of young adult novels that follow the lives of privileged high school students in Beverly Hills.
            2.The Clique series by Lisi Harrison – A series of novels that explore the complexities of teenage friendships and social cliques.
            Shows:

            1.Pretty Little Liars (2010) – A teen drama mystery series that follows a group of friends being haunted by a mysterious figure.
            2.90210 (2008) – A teen drama series that explores the lives of wealthy high school students in Beverly Hills, navigating love, friendships, and scandals.
            -------------------------------------------------------------------------------------------------------------------------
            

            Use the above as examples. And follow the following format for your responses of each type of media Make it well spaced and readable.

            Format:
            Movies:
            1.Title (Year) – 

            Director, 

            Cast: [Main actors], 

            <Brief description in 2-3 lines>
            <newline>

            <Link to Google search>
            <newline>

            <Link to Letterboxed>

            2.Title (Year) – 

            Director, 

            Cast: [Main actors], 

            <Brief description in 2-3 lines>
            <newline>
            <Link to Google search>
            <newline>

            <Link to Letterboxed>


            Books:
            1.Title (Author) – 
            Brief description in 2-3 lines.
            <Link>

            TV Shows:
            1.Title (Year) – 
            Brief description in 2-3 lines.
            <Link to Google search>

            Using the reference media text and it's year(optional), find books, movies, or TV shows that are relevant to the question asked. 
            Only find media that is present in the Search Options List (e.g., Books, Movies, Shows).
            Ensure the recommendations align with the attributes mentioned in the query (e.g., same actress, director, genre, or theme). 
            Return only relevant results based on the provided reference media.

            Reference Media: {referencemedia}
            Year: {year if year else 'Any'}
            Search Options: {searchoptions}
            Question: {query}
            Answer:
            """
    
        prompt_json = [{'role': 'user', 'content': llm_input_text}]
        chat_completion = self.client_together.chat.completions.create(model=LLM_MODEL_NAME,
                                                          messages=prompt_json,
                                                          temperature=0,
                                                          )
        response = chat_completion.choices[0].message.content
        return response, selected_node
    
    # @calculate_time
    def respond(self, query: str, ticker: str, year: str) -> tuple[str, TextNode]:
        """
        Given a questy, a ticker and a year, should return a response
        to the provided query for the given company in the given year and
        the most relevant node.
        """
        # Convert the given query string to a query bundle (most likely
        # required for correct work).
        # query_bundle = QueryBundle(query)

        query_embedding = self._embed_model.encode(query).tolist()

        # Initialize metadata filters.
        # metadata_filter = {"ticker": ticker, "year": year}

        metadata_filter = {
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"year": {"$eq": year}}
                ]
        }           

        # Initialize retriever from the vector store index
        # with the filters above and RETRIEVER_SIMILARITY_TOP_K.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=RETRIEVER_SIMILARITY_TOP_K,
            where=metadata_filter,
            include=["metadatas", "documents", "distances"]
        )
        
        # Retrieve the nodes for the provided query.
        retrieved_nodes = [
            TextNode(text=document, metadata=results["metadatas"][0][i])
            for i, document in enumerate(results["documents"][0])
        ]

        # print("Retrieved nodes:" + str(retrieved_nodes))
        # print(results['metadatas'][0])
        # Apply the reranker to the retrieved nodes and get
        # the best one.
        reranked_nodes = self.rerank(query, retrieved_nodes[:RERANKER_CHOICE_BATCH_SIZE])
        selected_node = reranked_nodes[0] if reranked_nodes else None
        print("Best retrieved node:" + str(selected_node.text) if selected_node else "No relevant context found.")

        # Merge the reranked nodes with the query and give it
        # to the LLM to get the response.
        # TODO
        llm_input_text = f"Answer the question given the context when possible. Keep in mind to return correct units when returning numerical data. Question: {query}\nContext: {selected_node.text if selected_node else 'No relevant context found.'}\nAnswer:"
    
        prompt_json = [{'role': 'user', 'content': llm_input_text}]
        chat_completion = self.client_together.chat.completions.create(model=LLM_MODEL_NAME,
                                                          messages=prompt_json,
                                                          temperature=0,
                                                          )
        response = chat_completion.choices[0].message.content
        return response, selected_node
    
    def rerank(self, query: str, retrieved_nodes: list) -> list:
        if not retrieved_nodes:
            return []
            
        pairs = [[query, node.text] for node in retrieved_nodes]
        
        scores = self.cross_encoder.predict(pairs)
        
        scored_nodes = list(zip(retrieved_nodes, scores))
        ranked_nodes = [node for node, score in sorted(scored_nodes, 
                                                     key=lambda x: -x[1])]
        
        return ranked_nodes[:RERANKER_TOP_N]



# Possible scores:
# [20 pts]        Basic RAG implemented, without metadata filtering
#                 and reranking.
# [+10 pts]       Metadata filtering implemented.
# [+5 pts]        Reranking implemented.
# [up to +10 pts] Manual evaluation implemented and analyzed.
