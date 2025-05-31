import importlib
import os
from core.logging import logger

SCRAPER_FOLDER = "app.scrapers"

def load_scrapers():
    """
    Recursively load all scraper modules from the scrapers folder and its subfolders.
    Only modules having a "main" function are loaded.
    The key for each module is set as the file name without extension.
    """
    scrapers = {}
    base_path = os.path.dirname(__file__)
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Build the module name
                rel_path = os.path.relpath(root, base_path)
                if rel_path == ".":
                    module_name = f"{SCRAPER_FOLDER}.{file[:-3]}"
                else:
                    rel_module = rel_path.replace(os.sep, ".")
                    module_name = f"{SCRAPER_FOLDER}.{rel_module}.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "main"):
                        key = file[:-3]  # Use the file name without extension as key
                        scrapers[key] = module
                        logger.info(f"Loaded scraper module: {module_name} as key: {key}")
                    else:
                        logger.warning(f"Module {module_name} does not have a 'main' function and was skipped.")
                except Exception as e:
                    logger.error(f"Error loading scraper module {module_name}: {e}", exc_info=True)
    return scrapers

SCRAPERS = load_scrapers()