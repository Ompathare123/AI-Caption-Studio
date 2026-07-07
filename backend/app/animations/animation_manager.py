import hashlib
import json
from typing import Any, Dict, List

from backend.app.animations.animation_engine import AnimationEngine
from backend.app.core.logging import logger
from backend.app.schemas.caption_style import StyleProperties


class AnimationManager:
    # Memory cache for generated animations to avoid redundant math recalculations
    _cache: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def _generate_cache_key(
        cls,
        subtitles: List[Dict[str, Any]],
        style: StyleProperties,
        preset: str,
    ) -> str:
        # Generate an MD5 hash of subtitle inputs, style configs, and preset code
        subs_str = json.dumps(subtitles, sort_keys=True)
        style_str = json.dumps(style.model_dump(), sort_keys=True)
        combined = f"{subs_str}:{style_str}:{preset}"
        return hashlib.md5(combined.encode("utf-8")).hexdigest()

    @classmethod
    def get_animated_timeline(
        cls,
        subtitles: List[Dict[str, Any]],
        style: StyleProperties,
        preset: str,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves animated subtitles list from memory cache if available,
        otherwise compiles and saves them.
        """
        cache_key = cls._generate_cache_key(subtitles, style, preset)

        if cache_key in cls._cache:
            logger.info(f"Animation cache HIT for preset '{preset}'")
            return cls._cache[cache_key]

        logger.info(
            f"Animation cache MISS for preset '{preset}' - executing timeline compile..."
        )
        animated_subtitles = AnimationEngine.generate_animation_timeline(
            subtitles=subtitles, style=style, preset=preset
        )

        # Protect against memory growth leaks by clearing cache if too large
        if len(cls._cache) >= 200:
            cls._cache.clear()

        cls._cache[cache_key] = animated_subtitles
        logger.info(
            f"Animation timeline generated and saved in cache key: {cache_key}"
        )
        return animated_subtitles
