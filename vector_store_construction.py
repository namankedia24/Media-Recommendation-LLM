# import os
# import re

# from llama_index.core.schema import TextNode
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import chromadb
# from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer

# from config import PROCESSED_DATA_DIR, VECTOR_STORE_DIR, EMBED_MODEL_NAME

# # TODO: take all the documents from PROCESSED_DATA_DIR, chunk them and
# # store them in a vector database with a corresponding vector store index.
# # This requires implementing get_all_nodes and get_file_chunks for
# # chunking the documents and filling out the 'main'.

# # We suggest sticking to the provided template for we believe it to be
# # the simplest implementation way. Please, provide explanation if you
# # find it necessary to change template.

# # Get the embedding model for the vector store index given EMBED_MODEL_NAME.



# embed_model = EMBED_MODEL_NAME 
# # client = chromadb.Client(Settings(
# #     persist_directory=VECTOR_STORE_DIR,  # Path to persist the database
# #     chroma_db_impl="duckdb+parquet"      # Backend implementation
# # ))

# client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)

# # Create or load a collection in ChromaDB
# collection_name = "final"
# collection = client.get_or_create_collection(name=collection_name)

# # Load embedding model
# embed_model = SentenceTransformer(EMBED_MODEL_NAME)



# def get_file_chunks(file_dir: str) -> list[str] | list[TextNode]:
#     """
#     Given a {ticker}_{year} directory, this method should read the file in there
#     and chunk it. The choice of chunking strategy is a part of this task. The most
#     basic chunking (using SentenceSplitter) is valued 10 points. More advanced methods
#     are valued up to 5 points.
#     """
#     chunks = []
#     chunk_size = 500  # Maximum number of characters per chunk

#     file_path = os.path.join(file_dir, "content.txt")
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return chunks
#     print(f"Reading file: {file_path}")
#     with open(file_path, 'r', encoding='utf-8') as f:
#         content = f.read()


#     #ADVANCED CHUNKING STRATEGY
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50,
#         separators=["\n\n", "\n", ".", " "]
#     )
    
#     chunks = splitter.split_text(content)
    
#     # Convert chunks to TextNode objects
#     text_chunks = []
#     for chunk in chunks:
#         text_chunks.append(TextNode(text=chunk.strip()))
        
#     return text_chunks
#     # print(content[:1000])
#     # Basic chunking using paragraphs for logical boundaries
#     # paragraphs = content.split("\n")
#     # # print(len(paragraphs))
#     # current_chunk = ""
    
#     # for paragraph in paragraphs:
#     #     if len(current_chunk) + len(paragraph) > chunk_size:
#     #         # Save current chunk as a TextNode
#     #         current_chunk = re.sub(r'\s+', ' ', current_chunk).strip()
#     #         chunks.append(TextNode(text=current_chunk))
#     #         current_chunk = paragraph  # Start a new chunk
#     #     else:
#     #         current_chunk += "\n" + paragraph

#     # # Add the last chunk if it exists
#     # if current_chunk.strip():
#     #     chunks.append(TextNode(text=current_chunk.strip()))

#     # # print(chunks[0])
#     # return chunks


# def get_all_nodes(filings_dir: str) -> list[TextNode]:
#     """
#     Given the filings directory, it should go over the {ticker}_{year} directories
#     and get chunks for each of them using get_file_chunks methods, followed by
#     creating TextNode instances for each chunk (if they are not already created --
#     that will depend on the get_file_chunks implementation) and adding metadata 
#     as dictionary: {'ticker': [ticker], 'year': [year]}.
#     """
#     # TODO
#     all_nodes = []
#     count = 10
#     for entry in os.listdir(filings_dir):
#         entry_path = os.path.join(filings_dir, entry)
#         if os.path.isdir(entry_path):
#             # Extract ticker and year from directory name (e.g., "BA_2011")
#             match = entry.split("_")
#             if len(match) == 2:
#                 ticker, year = match
#                 chunks = get_file_chunks(entry_path)
#                 for chunk in chunks:
#                     chunk.metadata = {"ticker": ticker, "year": year}
#                     all_nodes.append(chunk)
#             else:
#                 print(f"Invalid directory format: {entry}")
#         if count == 0:
#             break
#         count -= 1

#     return all_nodes


# def store_nodes_in_chromadb(all_nodes: list[TextNode]):
#     ids = []
#     embeddings = []
#     metadatas = []
#     documents = []

#     for idx, node in enumerate(all_nodes):
#         content = node.text
#         metadata = node.metadata
        
#         # Generate embedding for the content
#         embedding = embed_model.encode(content).tolist()
        
#         # Create unique ID for each node
#         node_id = f"{metadata['ticker']}_{metadata['year']}_{idx}"
#         # print("Creating node:", node_id)
        
#         ids.append(node_id)
#         embeddings.append(embedding)
#         metadatas.append(metadata)
#         documents.append(content)

#     print("Adding nodes to ChromaDB...")
#     batch_size = 35000
#     for i in range(0, len(ids), batch_size):
#         end_idx = min(i + batch_size, len(ids))
#         print(f"Adding batch {i//batch_size + 1}: documents {i} to {end_idx}")
        
#         collection.add(
#             ids=ids[i:end_idx],
#             embeddings=embeddings[i:end_idx],
#             metadatas=metadatas[i:end_idx],
#             documents=documents[i:end_idx]
#         )

#     print("Finished adding all documents to ChromaDB")
    
#     print(f"Stored {len(ids)} nodes in ChromaDB.")

# # THIS IS JUST A TEST FUNCTION NOT FOR THE RAG RETREIVAL SYSTEM 
# def query_chromadb(query_text, top_k=7):
#     # Generate embedding for the query text
#     query_embedding = embed_model.encode(query_text).tolist()
    
#     # Query ChromaDB collection
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k,
#         include=["metadatas", "documents"]
#     )
    
#     return results


# if __name__ == '__main__':

#     all_nodes = get_all_nodes(PROCESSED_DATA_DIR)
#     print(len(all_nodes))

#     print("Storing nodes in ChromaDB...")
#     store_nodes_in_chromadb(all_nodes)



#     # query_text = "What were Boeing's revenues in 2015?"
    
#     # print("Querying ChromaDB...")
#     # results = query_chromadb(query_text)

#     # # print(results)
    
#     # print("Top Results:")
#     # for i, document in enumerate(results["documents"][0]):
#     #     metadata = results["metadatas"][0][i]
#     #     print(f"Result {i + 1}:")
#     #     print(f"Metadata: {metadata}")
#     #     print(f"Content: {document[:2000]}...\n") 
    


#     # TODO: initialize a database which stores all_nodes in VECTOR_STORE_DIR
#     # and a corresponding vector store index. We recommend ChromaDB.

# # Possible scores:
# # [15 pts]       Chunks are obtained using SentenceSplitter and stored
# #                in a vector database in VECTOR_STORE_DIR.
# # [<15 pts]      Some mistakes exist (full documents are store in the
# #                vector database, the directory is wrong, etc.).
# # [up to +5 pts] An advanced chunking method is applied
# #                (better than SentenceSplitter).
