import logging
import os
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from database.db_client import DBClient
from services.aggregator_llm import AggregatorLLM
from services.chunker import Chunker
from services.dbscan_category import DBSCANCategory
from services.embedder import Embedder
from services.multi_llm_runner import run_multi_llm
from services.retriever import Retriever
from services.text_preprocessor import TextPreprocessor
from vectorstore.vector_manager import VectorManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FullPipeline:
    """End-to-end orchestration across ingestion, retrieval, and reasoning."""

    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.vector_manager = VectorManager(db_type=os.getenv("VECTOR_DB", "faiss"))
        self.dbscan_category = DBSCANCategory()
        self.retriever = Retriever(self.vector_manager, self.embedder)
        self.aggregator = AggregatorLLM()
        self.db_client = DBClient()

        # Maintain corpus level state for clustering analytics
        self._all_chunks: List[str] = []
        self._all_embeddings: List[np.ndarray] = []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            content = self._get_content(input_data)
            if not content:
                raise ValueError("No content to process")

            chunk_size = int(input_data.get("chunk_size", self.chunker.chunk_size))
            chunk_overlap = int(input_data.get("chunk_overlap", self.chunker.overlap))
            lowercase = bool(input_data.get("lowercase", True))
            deduplicate = bool(input_data.get("deduplicate", True))

            self.chunker.configure(chunk_size=chunk_size, overlap=chunk_overlap)
            self.text_preprocessor.configure(lowercase=lowercase, deduplicate=deduplicate)

            cleaned_text = self.text_preprocessor.preprocess(content)
            chunks = self.chunker.chunk(cleaned_text)
            if not chunks:
                raise ValueError("No chunks were produced from the input")

            embeddings = self.embedder.embed(chunks)

            doc_id = input_data.get("doc_id") or input_data.get("id") or f"doc_{abs(hash(content))}"
            metadata = input_data.get("metadata", {})
            metadata_list = [{
                **metadata,
                "source": input_data.get("source", "upload"),
                "doc_id": doc_id,
                "chunk_index": idx
            } for idx, _ in enumerate(chunks)]
            self.vector_manager.add_embeddings(documents=chunks, embeddings=embeddings, metadata=metadata_list)

            self._all_chunks.extend(chunks)
            self._all_embeddings.append(embeddings)
            stacked_embeddings = np.vstack(self._all_embeddings) if self._all_embeddings else embeddings
            self.dbscan_category.update_clusters(stacked_embeddings, self._all_chunks)

            return {
                "status": "success",
                "message": f"Processed and stored {len(chunks)} chunks.",
                "chunks": len(chunks)
            }

        except Exception as exc:
            logger.exception("Pipeline ingestion failed")
            return {"status": "error", "message": str(exc)}

    def query(
        self,
        query_text: str,
        *,
        top_k: int = 5,
        selected_models: Optional[Sequence[str]] = None,
        aggregator_enabled: bool = True,
        api_keys: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            retrieved_chunks = self.retriever.retrieve(query_text, top_k=top_k)
            multi_llm_answers = run_multi_llm(query_text, retrieved_chunks, selected_models, api_keys)

            aggregator_summary = None
            if aggregator_enabled:
                aggregator_summary = self.aggregator.aggregate(query_text, multi_llm_answers)
            final_answer = aggregator_summary or (multi_llm_answers[0]["response"] if multi_llm_answers else "")

            query_embedding = self.embedder.embed_query(query_text)
            category_id, category_score = self.dbscan_category.classify(query_embedding)

            self.db_client.save_query(query_text, final_answer, multi_llm_answers)

            metrics = {
                "models": multi_llm_answers,
                "category": {
                    "id": int(category_id) if category_id != -1 else None,
                    "score": round(float(category_score), 3) if category_score else None
                }
            }

            return {
                "status": "success",
                "question": query_text,
                "final_answer": final_answer,
                "multi_llm_answers": multi_llm_answers,
                "retrieved_chunks": retrieved_chunks,
                "metrics": metrics
            }

        except Exception as exc:
            logger.exception("Query pipeline failed")
            return {"status": "error", "message": str(exc)}

    def _get_content(self, input_data: Dict[str, Any]) -> Optional[str]:
        if "text" in input_data and input_data["text"]:
            return input_data["text"]
        if "file_path" in input_data and input_data["file_path"]:
            from services.file_parser import extract_text_from_file
            return extract_text_from_file(input_data["file_path"], "")
        if "url" in input_data and input_data["url"]:
            try:
                import requests
                response = requests.get(input_data["url"], timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as exc:
                logger.warning("Failed to fetch URL content: %s", exc)
        return None
