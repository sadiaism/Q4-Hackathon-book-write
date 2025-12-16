import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ConfigValidator:
    """
    Utility class for validating configuration and environment variables
    """

    @staticmethod
    def validate_required_env_vars(required_vars: List[str]) -> Dict[str, Any]:
        """
        Validate that all required environment variables are set.

        Args:
            required_vars: List of required environment variable names

        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "missing_vars": [],
            "validation_details": {}
        }

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                results["valid"] = False
                results["missing_vars"].append(var)
                results["validation_details"][var] = {
                    "present": False,
                    "value": None
                }
            else:
                results["validation_details"][var] = {
                    "present": True,
                    "value": "****" if "KEY" in var or "SECRET" in var or "PASSWORD" in var else value
                }

        if not results["valid"]:
            logger.error(f"Missing required environment variables: {results['missing_vars']}")
        else:
            logger.info("All required environment variables are present")

        return results

    @staticmethod
    def validate_api_keys() -> bool:
        """
        Validate that required API keys are set.

        Returns:
            True if all required API keys are present, False otherwise
        """
        required_keys = ["GEMINI_API_KEY", "COHERE_API_KEY"]
        validation_result = ConfigValidator.validate_required_env_vars(required_keys)

        return validation_result["valid"]

    @staticmethod
    def validate_qdrant_config() -> bool:
        """
        Validate Qdrant configuration.

        Returns:
            True if Qdrant is properly configured, False otherwise
        """
        # Either both URL and API key are set, or just the URL, or we'll use local
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if qdrant_url:
            logger.info(f"Qdrant configured with URL: {qdrant_url}")
            return True
        else:
            logger.info("Qdrant configured to use local instance")
            return True  # Local instance is valid

    @staticmethod
    def validate_all_configs() -> Dict[str, Any]:
        """
        Validate all configurations.

        Returns:
            Dictionary with overall validation results
        """
        logger.info("Validating all configurations...")

        api_keys_valid = ConfigValidator.validate_api_keys()
        qdrant_valid = ConfigValidator.validate_qdrant_config()

        results = {
            "overall_valid": api_keys_valid and qdrant_valid,
            "api_keys_valid": api_keys_valid,
            "qdrant_valid": qdrant_valid,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }

        if results["overall_valid"]:
            logger.info("All configurations are valid")
        else:
            logger.error("Some configurations are invalid")

        return results