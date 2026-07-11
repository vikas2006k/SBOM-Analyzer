import json
import csv

class ParserHelper:
    """Utility helper containing safe handlers for CSV and JSON input streams."""

    @staticmethod
    def load_json(file_path):
        """Safely load and parse JSON files content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as jde:
            raise ValueError(f"Invalid JSON file format: {str(jde)}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Source file not found: {file_path}")

    @staticmethod
    def load_csv(file_path):
        """Safely parse CSV file content into list of dictionaries."""
        parsed_rows = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parsed_rows.append(dict(row))
            return parsed_rows
        except csv.Error as ce:
            raise ValueError(f"Invalid CSV file format: {str(ce)}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Source file not found: {file_path}")
