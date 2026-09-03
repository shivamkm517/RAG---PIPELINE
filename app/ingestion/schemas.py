from pydantic import BaseModel, Field
from typing import Optional

class ChunkMetadata(BaseModel):
    """
    Metadata for a chunk of data.
    """
    doc_id : str = Field(..., description="The unique identifier for the document.")
    title: str
    section : Optional[str] = None
    page_number: Optional[int] = Field(None, description="The page number of the document this chunk belongs to.")

class DocumentChunk(BaseModel):
    """
    A chunk of a document, containing text and associated metadata.
    """

    chunk_id: str = Field(..., description="The unique identifier for the chunk.")
    text: str = Field(..., description="The text content of the chunk.")
    metadata: ChunkMetadata = Field(..., description="Metadata associated with the chunk.")