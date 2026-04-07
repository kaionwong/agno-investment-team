"""
Database Session
----------------

PostgreSQL database connection for AgentOS.
"""

from os import getenv
from typing import Any, Dict, List

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from db.url import db_url

OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL", "http://localhost:11434")

DB_ID = "investment-team-db"


class _FixedOllamaEmbedder(OllamaEmbedder):
    """Subclass that omits the unsupported `dimensions` kwarg from Ollama's embed call."""

    def _response(self, text: str) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        if self.options is not None:
            kwargs["options"] = self.options
        # NOTE: Do NOT pass dimensions — ollama Python client 0.4.x doesn't support it
        response = self.client.embed(input=text, model=self.id, **kwargs)
        if response and "embeddings" in response:
            embeddings = response["embeddings"]
            if isinstance(embeddings, list) and len(embeddings) > 0 and isinstance(embeddings[0], list):
                return {"embeddings": embeddings[0]}
            elif isinstance(embeddings, list) and all(isinstance(x, (int, float)) for x in embeddings):
                return {"embeddings": embeddings}
        return {"embeddings": []}

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self._response(text=text)
            embedding = response.get("embeddings", [])
            # Skip dimension check if no embedding returned; let caller handle it
            if not embedding:
                return []
            if self.dimensions is not None and len(embedding) != self.dimensions:
                from agno.utils.log import logger
                logger.warning(f"Expected {self.dimensions} dims, got {len(embedding)}")
                return []
            return embedding
        except Exception as e:
            from agno.utils.log import logger
            logger.warning(e)
            return []


def get_postgres_db(contents_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Args:
        contents_table: Optional table name for storing knowledge contents.

    Returns:
        Configured PostgresDb instance.
    """
    if contents_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=contents_table)
    return PostgresDb(id=DB_ID, db_url=db_url)


def create_knowledge(name: str, table_name: str) -> Knowledge:
    """Create a Knowledge instance with PgVector keyword search without embeddings.

    Args:
        name: Display name for the knowledge base.
        table_name: PostgreSQL table name for storage.

    Returns:
        Configured Knowledge instance.
    """
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=_FixedOllamaEmbedder(
                id="nomic-embed-text",
                dimensions=768,
                host=OLLAMA_BASE_URL,
            ),
        ),
        contents_db=get_postgres_db(contents_table=f"{table_name}_contents"),
    )
