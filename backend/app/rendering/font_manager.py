import os
from PIL import ImageFont

from backend.app.core.logging import logger


class FontManager:
    _font_path_cache = {}
    _loaded_fonts = {}

    @classmethod
    def get_font_file(cls, font_name: str) -> str:
        """
        Locates the absolute file path of a TTF/OTF font by searching standard
        OS system paths recursively.
        """
        font_clean = font_name.lower().strip()
        if font_clean in cls._font_path_cache:
            return cls._font_path_cache[font_clean]

        # Map clean styles config names to actual typical system filenames
        font_files = {
            "arial": ["arial.ttf", "Arial.ttf"],
            "arial black": ["ariblk.ttf", "Arial Black.ttf"],
            "impact": ["impact.ttf", "Impact.ttf"],
            "georgia": ["georgia.ttf", "Georgia.ttf"],
            "times new roman": ["times.ttf", "Times New Roman.ttf"],
            "roboto": ["Roboto-Regular.ttf", "roboto.ttf"],
            "montserrat": ["Montserrat-Regular.ttf", "montserrat.ttf"],
            "helvetica": ["helvetica.ttf", "Helvetica.ttf"],
            "helvetica neue": ["HelveticaNeue.ttf", "helveticaneue.ttf"],
            "proxima nova": ["ProximaNova-Regular.otf", "Proxima Nova.ttf"],
            "futura": ["futura.ttf", "Futura.ttf"],
            "futura extra bold": ["FuturaExtraBold.ttf", "futurab.ttf"],
            "orbitron": ["Orbitron-Regular.ttf", "orbitron.ttf"],
        }

        # System default folders
        search_paths = []
        if os.name == "nt":  # Windows
            search_paths.append(r"C:\Windows\Fonts")
        search_paths.extend(
            [
                "/Library/Fonts",
                "/System/Library/Fonts",
                "/usr/share/fonts",
                "/usr/share/fonts/truetype",
                "~/.fonts",
            ]
        )

        names_to_try = font_files.get(
            font_clean, [f"{font_name}.ttf", f"{font_name}.otf"]
        )

        for base_path in search_paths:
            expanded = os.path.expanduser(base_path)
            if os.path.exists(expanded):
                # Search up to 3 levels deep
                for root, _, files in os.walk(expanded):
                    for file in files:
                        for name in names_to_try:
                            if file.lower() == name.lower():
                                path = os.path.join(root, file)
                                cls._font_path_cache[font_clean] = path
                                return path

        # Try default Windows path directly as final NT safeguard
        if os.name == "nt":
            fallback_arial = r"C:\Windows\Fonts\arial.ttf"
            if os.path.exists(fallback_arial):
                cls._font_path_cache[font_clean] = fallback_arial
                return fallback_arial

        logger.warning(
            f"Font '{font_name}' not resolved in system paths. Using fallback."
        )
        return ""

    @classmethod
    def load_truetype_font(cls, font_name: str, size: float) -> ImageFont:
        """
        Load and cache Pillow ImageFont instances to prevent file load bottlenecks.
        """
        size_int = max(1, int(round(size)))
        font_file = cls.get_font_file(font_name)

        cache_key = (font_file, size_int)
        if cache_key in cls._loaded_fonts:
            return cls._loaded_fonts[cache_key]

        try:
            if font_file:
                font = ImageFont.truetype(font_file, size_int)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            logger.error(
                f"Failed to load font {font_name} from {font_file}: {str(e)}"
            )
            # Default PIL bitmap fallback font
            font = ImageFont.load_default()

        cls._loaded_fonts[cache_key] = font
        return font
