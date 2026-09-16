"""
    Long-term "reflection" memory for learning agents.

    Each agent has its own ChromaDB collection. After a trade's outcome
    is known, the market sitution and the cooresponding lession can be 
    stored and later retrieved when a similar sitution occurs.
"""
#============================================================================
#                                Import Statements
#============================================================================

import chromadb
from langchain_ollama import OllamaEmbeddings
from config import EMBEDDING_MODEL

#============================================================================
#                                Class Statements
#============================================================================

class FinancialSituationMemory:
    def __init__(self , name:str):
        """
            Iitialize a financial situation memory.
            Args:
                name : Name of the ChromaDB Collection
                config : Application configuration dictionary.
        """

        # Ollama embedding model 
        self.embedding_model = EMBEDDING_MODEL
        self.embeddings = OllamaEmbeddings(model = self.embedding_model)

        # ChromaDB
        self.chroma_client = chromadb.Client(chromadb.config.Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.get_or_create_collection(name=name)


    # Create Embedding
    def get_embedding(self , text: str) -> list[float]:
        """
            Generate an embedding using Ollama local
            nomic-embed-text model
        """
        return self.embeddings.embed_query(text)

    # Add Situations
    def add_situations(self , situations_and_advice : list[tuple[str,str]]) -> None:
        """
            Add financial situations and recommendations to memory.
            Args:
                situations_and_advice:
                    list of tuples:
                    (
                        situation_text , recommendation_text
                    )
        """
        if not situations_and_advice:
            return 

        # Get current document count to generate unique IDs
        offset = self.situation_collection.count()
        ids = [
            str(offset + i) 
            for i , _ in enumerate(situations_and_advice)
        ]

        # Extract situations
        situations = [situation for situation , _ in situations_and_advice]

        # Extract recommendations
        recommendations = [recommendation for _ , recommendation in situations_and_advice]

        # Generate Embeddings
        embeddings = [self.get_embedding(situation) for situation in situations]

        # Store everything in chromaDB
        self.situation_collection.add(documents=situations,metadatas=[
            {
                "recommendation" : recommendation
            } 
            for recommendation in recommendations
        ],
        embeddings=embeddings , ids = ids 
        )

    # Retrieve memories
    def get_memories(self , current_situation : str , n_matches : int = 1) -> list[dict]:
        """
            Retrieve recoomendations from similar past situations.
        """

        # No memories available
        if self.situation_collection.count() == 0:
            return []

        # Generate embedding for current situation
        query_embedding = self.get_embedding(current_situation)

        # Search ChromaDB
        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_matches , self.situation_collection.count()),
            include=[
                "meta",
                "documents",
                "distances"
            ]
        )

        # Format results
        memories = []

        for document, metadata , distance in zip(
            results['documents'][0],results['metadatas'][0],results['distances'][0]
        ):
            memories.append(
                {
                    "situation" : document,
                    "recommendation" : metadata['recommendation'],
                    "distance" : distance 
                }
            )

        return memories 


# Build memories 
def build_memories()-> dict[str , FinancialSituationMemory]:
    """
        Create one memory store for each learning agent.
    """
    return {
        "bull_memory" : FinancialSituationMemory("bull_memory"),
        "bear_memory" : FinancialSituationMemory("bear_memory"),
        "trader_memory" : FinancialSituationMemory("trader_memory"),
        "invest_judge_memory" : FinancialSituationMemory("invest_judge_memory"),
        "risk_manager_memory" : FinancialSituationMemory("risk_manager_memory")
    }

