"""
API Routes for Text and Table Content Builder
=============================================

FastAPI routes for content generation endpoints.
"""

import logging
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException, status

from models.requests import (
    TextGenerationRequest,
    TableGenerationRequest,
    BatchTextGenerationRequest,
    BatchTableGenerationRequest
)
from models.responses import (
    GeneratedText,
    GeneratedTable,
    BatchTextGenerationResponse,
    BatchTableGenerationResponse,
    HealthResponse,
    SessionInfoResponse
)
from core.generators import TextGenerator, TableGenerator
from core.session_manager import get_session_manager
from core.llm_client import get_llm_client, LLMClientFactory


logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


# Health and Status Endpoints

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and configuration.
    """
    try:
        llm_client = get_llm_client()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            service="text-table-builder",
            llm_provider=llm_client.__class__.__name__.replace("Client", "").lower(),
            llm_model=llm_client.model
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/", tags=["Info"])
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "Text and Table Content Builder",
        "version": "1.0.0",
        "description": "LLM-powered content generation for presentations",
        "endpoints": {
            "health": "/health",
            "text": "/generate/text",
            "table": "/generate/table",
            "batch_text": "/generate/batch/text",
            "batch_table": "/generate/batch/table",
            "docs": "/docs"
        },
        "providers_available": LLMClientFactory.get_available_providers()
    }


# Text Generation Endpoints

@router.post(
    "/generate/text",
    response_model=GeneratedText,
    tags=["Generation"],
    summary="Generate text content",
    description="Generate HTML-formatted text content from topics and narrative"
)
async def generate_text(request: TextGenerationRequest):
    """
    Generate text content for a slide.

    This endpoint generates rich HTML text content based on:
    - Key topics to cover
    - Overall narrative/story
    - Presentation context (theme, audience, title)
    - Word count constraints
    - Previous slides context (for flow)

    Returns GeneratedText with HTML content and metadata.
    """
    try:
        logger.info(f"Text generation request for slide {request.slide_id}")

        generator = TextGenerator()
        result = await generator.generate(request)

        logger.info(
            f"Text generated for {request.slide_id}: "
            f"{result.metadata['word_count']} words"
        )

        return result

    except Exception as e:
        logger.error(f"Text generation failed for {request.slide_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


@router.post(
    "/generate/batch/text",
    response_model=BatchTextGenerationResponse,
    tags=["Generation"],
    summary="Generate multiple text contents",
    description="Batch generate text content for multiple slides"
)
async def generate_batch_text(batch_request: BatchTextGenerationRequest):
    """
    Generate text content for multiple slides in batch.

    Processes requests in parallel if batch_request.parallel is True.
    Maintains session context across all slides.

    Returns BatchTextGenerationResponse with all results and metadata.
    """
    try:
        logger.info(
            f"Batch text generation: {len(batch_request.requests)} slides "
            f"(parallel: {batch_request.parallel})"
        )

        generator = TextGenerator()

        if batch_request.parallel:
            # Process in parallel
            tasks = [
                generator.generate(req)
                for req in batch_request.requests
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            successes = []
            failures = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failures.append({
                        "slide_id": batch_request.requests[i].slide_id,
                        "error": str(result)
                    })
                else:
                    successes.append(result)

            metadata = {
                "total_requested": len(batch_request.requests),
                "successful": len(successes),
                "failed": len(failures),
                "failures": failures if failures else None
            }

            return BatchTextGenerationResponse(
                results=successes,
                metadata=metadata
            )

        else:
            # Process sequentially
            results = []
            for req in batch_request.requests:
                try:
                    result = await generator.generate(req)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to generate text for {req.slide_id}: {e}")
                    # Continue with other requests

            metadata = {
                "total_requested": len(batch_request.requests),
                "successful": len(results),
                "failed": len(batch_request.requests) - len(results)
            }

            return BatchTextGenerationResponse(
                results=results,
                metadata=metadata
            )

    except Exception as e:
        logger.error(f"Batch text generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch text generation failed: {str(e)}"
        )


# Table Generation Endpoints

@router.post(
    "/generate/table",
    response_model=GeneratedTable,
    tags=["Generation"],
    summary="Generate table content",
    description="Generate HTML table from data and description"
)
async def generate_table(request: TableGenerationRequest):
    """
    Generate table content for a slide.

    This endpoint generates HTML tables based on:
    - Description of what the table should show
    - Raw data (optional - LLM can structure optimally)
    - Presentation context (theme, audience, title)
    - Table constraints (max rows, max columns)
    - Previous slides context (for flow)

    Returns GeneratedTable with HTML and metadata.
    """
    try:
        logger.info(f"Table generation request for slide {request.slide_id}")

        generator = TableGenerator()
        result = await generator.generate(request)

        logger.info(
            f"Table generated for {request.slide_id}: "
            f"{result.metadata['rows']}x{result.metadata['columns']}"
        )

        return result

    except Exception as e:
        logger.error(f"Table generation failed for {request.slide_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Table generation failed: {str(e)}"
        )


@router.post(
    "/generate/batch/table",
    response_model=BatchTableGenerationResponse,
    tags=["Generation"],
    summary="Generate multiple tables",
    description="Batch generate tables for multiple slides"
)
async def generate_batch_table(batch_request: BatchTableGenerationRequest):
    """
    Generate tables for multiple slides in batch.

    Processes requests in parallel if batch_request.parallel is True.
    Maintains session context across all slides.

    Returns BatchTableGenerationResponse with all results and metadata.
    """
    try:
        logger.info(
            f"Batch table generation: {len(batch_request.requests)} slides "
            f"(parallel: {batch_request.parallel})"
        )

        generator = TableGenerator()

        if batch_request.parallel:
            # Process in parallel
            tasks = [
                generator.generate(req)
                for req in batch_request.requests
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            successes = []
            failures = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failures.append({
                        "slide_id": batch_request.requests[i].slide_id,
                        "error": str(result)
                    })
                else:
                    successes.append(result)

            metadata = {
                "total_requested": len(batch_request.requests),
                "successful": len(successes),
                "failed": len(failures),
                "failures": failures if failures else None
            }

            return BatchTableGenerationResponse(
                results=successes,
                metadata=metadata
            )

        else:
            # Process sequentially
            results = []
            for req in batch_request.requests:
                try:
                    result = await generator.generate(req)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to generate table for {req.slide_id}: {e}")
                    # Continue with other requests

            metadata = {
                "total_requested": len(batch_request.requests),
                "successful": len(results),
                "failed": len(batch_request.requests) - len(results)
            }

            return BatchTableGenerationResponse(
                results=results,
                metadata=metadata
            )

    except Exception as e:
        logger.error(f"Batch table generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch table generation failed: {str(e)}"
        )


# Session Management Endpoints

@router.get(
    "/session/{presentation_id}",
    response_model=SessionInfoResponse,
    tags=["Session"],
    summary="Get session information",
    description="Retrieve information about a presentation session"
)
async def get_session_info(presentation_id: str):
    """
    Get session information for a presentation.

    Returns details about the session including:
    - Number of slides in context
    - Context size
    - Last update time
    - TTL remaining

    Useful for debugging and monitoring context retention.
    """
    try:
        session_manager = get_session_manager()
        session = await session_manager.get_session_context(presentation_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {presentation_id}"
            )

        # Calculate context size (rough estimate)
        import json
        context_json = session.model_dump_json()
        context_size = len(context_json.encode('utf-8'))

        return SessionInfoResponse(
            presentation_id=presentation_id,
            slides_in_context=len(session.slide_history),
            context_size_bytes=context_size,
            last_updated=session.last_updated.isoformat(),
            ttl_remaining_seconds=session_manager.default_ttl  # Simplified
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info for {presentation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.delete(
    "/session/{presentation_id}",
    tags=["Session"],
    summary="Delete session",
    description="Delete a presentation session and its context"
)
async def delete_session(presentation_id: str):
    """
    Delete a presentation session.

    Removes all context and slide history for the presentation.
    Use this to clean up after presentation is complete.

    Returns confirmation of deletion.
    """
    try:
        session_manager = get_session_manager()

        # Check if session exists
        session = await session_manager.get_session_context(presentation_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {presentation_id}"
            )

        # Delete session
        await session_manager.delete_session(presentation_id)

        return {
            "status": "success",
            "message": f"Session deleted: {presentation_id}",
            "slides_removed": len(session.slide_history)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {presentation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )
