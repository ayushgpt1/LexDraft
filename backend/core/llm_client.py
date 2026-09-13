import logging
from typing import Any

from google import genai

logger = logging.getLogger(__name__)


class ResilientGeminiClient:
    """
    Central Gemini client with model fallback.

    Primary model is tried first. If Gemini returns a transient
    provider/rate-limit error, the next model is attempted.
    """

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

        self.models = [
            "gemini-3.6-flash",
            "gemini-3.8-flash",
            "gemini-3.1-flash-lite",
        ]

    @staticmethod
    def _get_status_code(error: Exception):
        return getattr(error, "status_code", None) or getattr(error, "code", None)

    @classmethod
    def _is_retryable(cls, error: Exception) -> bool:
        status_code = cls._get_status_code(error)

        if status_code in {429, 500, 502, 503, 504}:
            return True

        message = str(error).lower()

        retryable_messages = [
            "503",
            "service unavailable",
            "unavailable",
            "high demand",
            "429",
            "resource exhausted",
            "rate limit",
            "too many requests",
            "internal server error",
            "bad gateway",
            "gateway timeout",
        ]

        return any(message_part in message for message_part in retryable_messages)

    def generate_content(
        self,
        contents: Any,
        config: Any = None,
    ):
        last_error = None

        for index, model in enumerate(self.models):
            try:
                logger.info(
                    "Gemini request using model=%s",
                    model,
                )

                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )

                if index > 0:
                    logger.warning(
                        "Gemini fallback succeeded using model=%s",
                        model,
                    )

                return response

            except Exception as error:
                last_error = error

                if not self._is_retryable(error):
                    raise

                logger.warning(
                    "Gemini model %s failed with retryable error: %s",
                    model,
                    error,
                )

                if index < len(self.models) - 1:
                    logger.info(
                        "Falling back from %s to %s",
                        model,
                        self.models[index + 1],
                    )

        raise RuntimeError(
            "All configured Gemini models failed. "
            "Please try again later."
        ) from last_error