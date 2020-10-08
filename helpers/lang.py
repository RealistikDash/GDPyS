import json
import os
from helpers.generalhelper import JsonFile
from config import user_config
from constants import Paths
from exceptions import LangNotFound

class Lang:
    def __init__(self, language : str = "en"):
        """Loads the given language."""
        self.text_find_msg = "Failed to find translated text for {}|{}"
        self.main_lang = language
        self.english_lang = JsonFile(Paths.lang_packs + "en.json").get_file() # English as a backup for when the main lang does not contain the str you're looking for.

        self.lang = JsonFile(Paths.lang_packs + language + ".json").get_file()

        # Check if lang is valid.
        if self.lang is None:
            raise LangNotFound

    def _format_string(self, text : str, format_args : tuple) -> str:
        """Formats a string according to the format args provided."""
        return text.format(*format_args)
    
    def _fail_find(self, type : str, text : str) -> str:
        """Creates a fail find str."""
        return self.text_find_msg.format(type, text)
    
    def _get_from_json(self, type : str, text : str) -> str:
        """Returns a string of given type from json."""
        text_category = self.lang.get(type)
        if text_category is None:
            text_category = self.english_lang.get(type)
            if text_category is None:
                return self._fail_find(type, text)
        
        new_text = text_category.get(text)
        if new_text is None:
            new_text = self.english_lang[type].get(text)
            if new_text is None:
                return self._fail_find(type, text)
        
        return new_text

    def _get_full(self, type : str, text : str, format_args : tuple = ()) -> str:
        """Gets full formatted translation from lang pack."""
        new_text = self._get_from_json(type, text)
        new_text = self._format_string(new_text, format_args)
        return new_text
    
    def warn(self, text : str, *args) -> str:
        """Translates a warn message."""
        return self._get_full("warning", text, args)
    
    def info(self, text : str, *args) -> str:
        """Translates a info message."""
        return self._get_full("info", text, args)
    
    def error(self, text : str, *args) -> str:
        """Translates a error message."""
        return self._get_full("errors", text, args)
    
    def debug(self, text : str, *args) -> str:
        """Translates a debug message."""
        return self._get_full("debug", text, args)
    
    def runtime(self, text : str, *args) -> str:
        """Translates a runtime message."""
        return self._get_full("runtime", text, args)
        
lang = Lang()