"""
Request Models for Text and Table Content Builder
==================================================

Pydantic models for incoming API requests from Content Orchestrator.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TextGenerationRequest(BaseModel):
    """
    Request model for text content generation.

    Matches Content Orchestrator's text request format.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier like 'slide_001'"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Content source
    topics: List[str] = Field(
        description="Key points to expand into full content"
    )
    narrative: str = Field(
        description="Overall narrative/story for this slide",
        default=""
    )

    # Context for generation
    context: Dict[str, Any] = Field(
        description="Presentation context (theme, audience, slide_title)",
        default_factory=dict
    )

    # Generation constraints
    constraints: Dict[str, Any] = Field(
        description="Generation constraints (max_characters, style, tone)",
        default_factory=dict
    )

    # Session context (optional - populated by session manager if not provided)
    previous_slides_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Context from previous slides for content flow"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_001",
                "slide_number": 1,
                "topics": ["Revenue growth", "Market expansion", "Cost efficiency"],
                "narrative": "Strong financial performance driven by strategic initiatives",
                "context": {
                    "theme": "professional",
                    "audience": "executives",
                    "slide_title": "Q3 Financial Results"
                },
                "constraints": {
                    "max_characters": 300,
                    "style": "professional",
                    "tone": "data-driven"
                }
            }
        }


class TableGenerationRequest(BaseModel):
    """
    Request model for table generation.

    LLM will analyze description and data to create optimal table structure.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Table specification
    description: str = Field(
        description="Description of what the table should display"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw data to be structured into table (can be dict, list, or nested)"
    )

    # Context
    context: Dict[str, Any] = Field(
        description="Presentation context",
        default_factory=dict
    )

    # Constraints
    constraints: Dict[str, Any] = Field(
        description="Table constraints (max_rows, max_columns, style)",
        default_factory=dict
    )

    # Session context
    previous_slides_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Context from previous slides"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_003",
                "slide_number": 3,
                "description": "Quarterly revenue breakdown by region showing Q2 vs Q3 comparison",
                "data": {
                    "Q2": {"North America": 45.2, "Europe": 32.1, "Asia": 28.7},
                    "Q3": {"North America": 58.3, "Europe": 39.4, "Asia": 35.6}
                },
                "context": {
                    "theme": "professional",
                    "audience": "executives",
                    "slide_title": "Regional Performance"
                },
                "constraints": {
                    "max_rows": 10,
                    "max_columns": 5,
                    "style": "clean"
                }
            }
        }


class BatchTextGenerationRequest(BaseModel):
    """
    Batch request for generating multiple text contents.
    """
    requests: List[TextGenerationRequest] = Field(
        description="List of text generation requests"
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process requests in parallel"
    )


class BatchTableGenerationRequest(BaseModel):
    """
    Batch request for generating multiple tables.
    """
    requests: List[TableGenerationRequest] = Field(
        description="List of table generation requests"
    )
    parallel: bool = Field(
        default=True,
        description="Whether to process requests in parallel"
    )
