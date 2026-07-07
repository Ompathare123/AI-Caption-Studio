import json
import os
from typing import Any, Dict, List
from pydantic import ValidationError

from backend.app.core.config import settings
from backend.app.core.errors import StyleNotFoundError, StyleValidationError
from backend.app.core.logging import logger
from backend.app.schemas.caption_style import StyleProperties


class StyleLoader:

    @staticmethod
    def get_style_filepath(style_name: str) -> str:
        """
        Scan and locate the JSON file path for a style name (checking custom first,
        then default).
        """
        name_clean = style_name.lower().strip()

        # 1. Check custom styles folder
        custom_path = os.path.join(
            settings.STYLES_DIR, "custom", f"{name_clean}.json"
        )
        if os.path.exists(custom_path):
            return custom_path

        # 2. Check predefined folders
        default_path = os.path.join(
            settings.STYLES_DIR, name_clean, f"{name_clean}.json"
        )
        if os.path.exists(default_path):
            return default_path

        raise StyleNotFoundError(
            f"Style configuration '{style_name}' not found on disk"
        )

    @staticmethod
    def load_style(style_name: str) -> Dict[str, Any]:
        """
        Load and validate a style JSON configuration.
        """
        logger.info(f"Style Load Request: '{style_name}'")
        filepath = StyleLoader.get_style_filepath(style_name)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Enforce validation schemas at runtime using Pydantic
            StyleProperties(**data)
            logger.info(
                f"Style Loaded and Validated successfully: '{style_name}'"
            )
            return data
        except json.JSONDecodeError as jde:
            logger.error(f"JSON decode failure in style '{style_name}': {str(jde)}")
            raise StyleValidationError(
                f"Invalid JSON formatting syntax in style file: {str(jde)}"
            )
        except ValidationError as ve:
            logger.error(
                f"Validation failed for style '{style_name}': {str(ve)}"
            )
            raise StyleValidationError(
                f"Style schema parameters validation failed: {str(ve)}"
            )
        except Exception as e:
            logger.error(f"Failed to load style '{style_name}': {str(e)}")
            if isinstance(e, (StyleNotFoundError, StyleValidationError)):
                raise e
            raise StyleValidationError(
                f"Unexpected style loading failure: {str(e)}"
            )

    @staticmethod
    def save_custom_style(style_name: str, style_data: Dict[str, Any]) -> str:
        """
        Validate and save a custom style JSON file to custom/ directory.
        """
        name_clean = style_name.lower().strip()
        if name_clean == "custom":
            raise StyleValidationError(
                "Cannot overwrite the base custom directory name definition"
            )

        logger.info(f"Style Save Request (Custom): '{style_name}'")
        try:
            # Enforce schema validation
            StyleProperties(**style_data)

            custom_dir = os.path.join(settings.STYLES_DIR, "custom")
            os.makedirs(custom_dir, exist_ok=True)

            filepath = os.path.join(custom_dir, f"{name_clean}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(style_data, f, indent=4)

            logger.info(f"Custom Style Saved successfully at {filepath}")
            return filepath
        except ValidationError as ve:
            logger.error(
                f"Custom Style validation failed for '{style_name}': {str(ve)}"
            )
            raise StyleValidationError(
                f"Custom style parameters validation failed: {str(ve)}"
            )
        except Exception as e:
            logger.error(
                f"Failed to save custom style '{style_name}': {str(e)}"
            )
            if isinstance(e, StyleValidationError):
                raise e
            raise StyleValidationError(
                f"Failed to export custom style file: {str(e)}"
            )

    @staticmethod
    def list_styles() -> List[str]:
        """
        List all available default and custom style names.
        """
        styles = set()

        # Scan default dirs
        if os.path.exists(settings.STYLES_DIR):
            for entry in os.listdir(settings.STYLES_DIR):
                entry_path = os.path.join(settings.STYLES_DIR, entry)
                if os.path.isdir(entry_path) and entry != "custom":
                    json_path = os.path.join(entry_path, f"{entry}.json")
                    if os.path.exists(json_path):
                        styles.add(entry)

        # Scan custom dir
        custom_dir = os.path.join(settings.STYLES_DIR, "custom")
        if os.path.exists(custom_dir):
            for file in os.listdir(custom_dir):
                if file.endswith(".json"):
                    styles.add(file[:-5])

        return sorted(list(styles))
