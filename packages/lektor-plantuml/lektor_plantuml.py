"""
Lektor plugin to render PlantUML diagrams from fenced code blocks.

Processes markdown code blocks with language "plantuml" and replaces
them with inline SVG images fetched from the PlantUML server.
"""

import zlib
import string
import requests
from lektor.pluginsystem import Plugin


# PlantUML uses a custom base64 alphabet
PLANTUML_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
BASE64_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"


def plantuml_encode(text):
    """
    Encode PlantUML text for the server URL.

    The encoding process:
    1. UTF-8 encode the text
    2. Deflate compress (raw deflate, no zlib header)
    3. Base64 encode with PlantUML's custom alphabet
    """
    # UTF-8 encode
    data = text.encode("utf-8")

    # Deflate compress (level 9, raw deflate without header)
    compressed = zlib.compress(data, 9)[2:-4]

    # Custom base64 encoding with PlantUML alphabet
    encoded = ""
    for i in range(0, len(compressed), 3):
        chunk = compressed[i:i+3]

        if len(chunk) == 3:
            b1, b2, b3 = chunk
            encoded += PLANTUML_ALPHABET[b1 >> 2]
            encoded += PLANTUML_ALPHABET[((b1 & 0x3) << 4) | (b2 >> 4)]
            encoded += PLANTUML_ALPHABET[((b2 & 0xF) << 2) | (b3 >> 6)]
            encoded += PLANTUML_ALPHABET[b3 & 0x3F]
        elif len(chunk) == 2:
            b1, b2 = chunk
            encoded += PLANTUML_ALPHABET[b1 >> 2]
            encoded += PLANTUML_ALPHABET[((b1 & 0x3) << 4) | (b2 >> 4)]
            encoded += PLANTUML_ALPHABET[(b2 & 0xF) << 2]
        elif len(chunk) == 1:
            b1 = chunk[0]
            encoded += PLANTUML_ALPHABET[b1 >> 2]
            encoded += PLANTUML_ALPHABET[(b1 & 0x3) << 4]

    return encoded


# In-memory cache for rendered SVGs
_svg_cache = {}


def fetch_plantuml_svg(text, server_url="http://www.plantuml.com/plantuml", timeout=120):
    """
    Fetch rendered SVG from PlantUML server.

    Uses in-memory caching to avoid re-fetching unchanged diagrams.
    
    Args:
        text: PlantUML diagram text
        server_url: PlantUML server URL
        timeout: Request timeout in seconds (default: 120)
    """
    # Check cache first
    cache_key = text.strip()
    if cache_key in _svg_cache:
        return _svg_cache[cache_key]

    encoded = plantuml_encode(text)
    url = f"{server_url}/svg/{encoded}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        svg = response.text

        # Cache the result
        _svg_cache[cache_key] = svg
        return svg
    except requests.RequestException as e:
        # Return error message as HTML comment + visible error
        error_msg = f'<div class="plantuml-error">PlantUML Error: {e}</div>'
        return error_msg


def make_plantuml_renderer_mixin(server_url, timeout=120):
    """
    Create a renderer mixin class that handles plantuml code blocks.
    
    Args:
        server_url: PlantUML server URL
        timeout: Request timeout in seconds
    """
    class PlantUMLRendererMixin:
        def block_code(self, code, lang=None):
            # mistune 0.8.x uses (self, code, lang=None)
            # mistune 2.x uses (self, code, info=None)
            # We use 'lang' to match mistune 0.8.x which is currently in use
            
            # Normalize the lang parameter
            if lang:
                lang = lang.strip()

            if lang == "plantuml":
                svg = fetch_plantuml_svg(code, server_url, timeout)
                return f'<div class="plantuml-diagram">{svg}</div>\n'

            # Delegate to the next class in MRO for non-plantuml blocks
            return super().block_code(code, lang)

    return PlantUMLRendererMixin


class PlantUMLPlugin(Plugin):
    name = "PlantUML"
    description = "Render PlantUML diagrams in markdown code blocks"

    def get_server_url(self):
        """Get PlantUML server URL from config or use default."""
        config = self.get_config()
        return config.get("server", "http://www.plantuml.com/plantuml")

    def get_timeout(self):
        """Get request timeout from config or use default (120 seconds)."""
        config = self.get_config()
        timeout = config.get("timeout", "120")
        try:
            return int(timeout)
        except ValueError:
            return 120

    def on_markdown_config(self, config, **extra):
        """Hook into markdown configuration to add our renderer mixin."""
        server_url = self.get_server_url()
        timeout = self.get_timeout()
        mixin = make_plantuml_renderer_mixin(server_url, timeout)
        # Insert at position 0 so our mixin is first in MRO and handles
        # plantuml blocks before other plugins (like markdown-highlighter)
        config.renderer_mixins.insert(0, mixin)
