"""
Utilities for content and metadata validation in retrieval testing
"""
import json
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher


def validate_content_accuracy(retrieved_text: str, original_text: str, threshold: float = 0.9) -> Dict[str, Any]:
    """
    Validate that retrieved text matches original text with specified accuracy threshold.

    Args:
        retrieved_text: Text retrieved from Qdrant
        original_text: Original text that was stored
        threshold: Minimum similarity ratio required (0-1)

    Returns:
        Dictionary with validation results
    """
    similarity_ratio = SequenceMatcher(None, retrieved_text.strip(), original_text.strip()).ratio()

    return {
        "content_matches": similarity_ratio >= threshold,
        "similarity_ratio": similarity_ratio,
        "threshold": threshold,
        "retrieved_text": retrieved_text,
        "original_text": original_text
    }


def validate_metadata(metadata: Dict[str, Any], expected_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate metadata fields (url, chunk_id) from Qdrant results.

    Args:
        metadata: Metadata from Qdrant result
        expected_metadata: Expected metadata values (optional)

    Returns:
        Dictionary with metadata validation results
    """
    required_fields = ["url", "chunk_id"]
    result = {
        "metadata_correct": True,
        "missing_fields": [],
        "field_validations": {}
    }

    # Check required fields exist
    for field in required_fields:
        if field not in metadata:
            result["metadata_correct"] = False
            result["missing_fields"].append(field)
        else:
            result["field_validations"][field] = {
                "exists": True,
                "value": metadata[field],
                "valid": True  # Basic validation - exists and is not None/empty
            }

            if not metadata[field]:
                result["metadata_correct"] = False
                result["field_validations"][field]["valid"] = False

    # If expected metadata provided, validate against it
    if expected_metadata:
        for field, expected_value in expected_metadata.items():
            if field in metadata:
                matches = metadata[field] == expected_value
                result["field_validations"][field]["matches_expected"] = matches
                if not matches:
                    result["metadata_correct"] = False

    return result


def format_test_result(query: str, results: List[Dict], validation: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
    """
    Format test results into clean JSON output.

    Args:
        query: Original query text
        results: Retrieved results from Qdrant
        validation: Validation results
        execution_time: Time taken for the test

    Returns:
        Formatted test result in clean JSON
    """
    return {
        "query": query,
        "execution_time": execution_time,
        "validation": validation,
        "results": [
            {
                "id": result.get("id"),
                "text": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", ""),  # Truncate long text
                "score": result.get("score"),
                "url": result.get("url"),
                "chunk_id": result.get("chunk_id")
            } for result in results
        ],
        "total_results": len(results)
    }


def clean_json_output(data: Any) -> str:
    """
    Convert data to clean, formatted JSON string.

    Args:
        data: Data to convert to JSON

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2, ensure_ascii=False)