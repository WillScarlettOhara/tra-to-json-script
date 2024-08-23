import os
import re
import sys
import chardet

def escape_quotes(text):
    """Escape double quotes in the text."""
    return text.replace('"', r"\"")
class TraFileParser:
    def __init__(self, file_path, encoding="utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self.tra_translations = {}

    def parse(self):
        """Parses the .tra file and stores translations."""
        try:
            with open(self.file_path, "r", encoding=self.encoding) as file:
                file_content = file.read()
                matches = re.findall(r"@(\d+)\s*=\s*~(.*?)~", file_content, re.DOTALL)
                for match in matches:
                    self.tra_translations[match[0]] = escape_quotes(match[1])
        except FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
        except UnicodeDecodeError:
            print(f"Error: Unable to decode file {self.file_path} with encoding {self.encoding}")

class PoFileParser:
    def __init__(self, file_path, encoding="utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self.po_translations = {}

    def parse(self):
        """Parses the .po file and stores translations."""
        try:
            with open(self.file_path, "r", encoding=self.encoding) as file:
                file_content = file.read()

                # Modified regex to handle escaped double quotes
                matches = re.findall(r'msgctxt "(.*?)"\s*msgid "(.*?)"\s*msgstr "(.*?)(?<!\\)"', file_content, re.DOTALL)
                for match in matches:
                    current_key = match[0]
                    # Unescape double quotes
                    msgstr = match[2].replace('\\"', '"').strip()
                    self.po_translations[current_key] = msgstr

        except FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
        except UnicodeDecodeError:
            print(f"Error: Unable to decode file {self.file_path} with encoding {self.encoding}")

class Converter:
    def __init__(self, base_name):
        self.base_name = base_name
        self.english_file_path = os.path.join("English", f"{self.base_name}.tra")
        self.french_file_path = os.path.join("French", f"{self.base_name}.tra")
        self.po_file_path = os.path.join("Finished_po", f"{self.base_name}.po")
        self.tra_file_path = os.path.join("Finished_tra", f"{self.base_name}.tra")

    def tra_to_po(self):
        """Converts a .tra file to a .po file."""
        # Detect and convert French file encoding if needed
        try:
            with open(self.french_file_path, "rb") as french_file:
                french_content = french_file.read()
                encoding = chardet.detect(french_content)["encoding"]
                if encoding != "utf-8":
                    print(f"Converting {self.french_file_path} from {encoding} to UTF-8...")
                    with open(self.french_file_path, "r", encoding=encoding) as french_file:
                        french_content = french_file.read()
                    with open(self.french_file_path, "w", encoding="utf-8") as french_file:
                        french_file.write(french_content)
        except FileNotFoundError:
            print(f"Error: French file not found: {self.french_file_path}")
            return
        except UnicodeDecodeError:
            print(f"Error: Unable to decode French file: {self.french_file_path}")
            return

        # Parse .tra files
        english_parser = TraFileParser(self.english_file_path)
        english_parser.parse()
        french_parser = TraFileParser(self.french_file_path, encoding="utf-8")
        french_parser.parse()

        # Create the .po file
        try:
            with open(self.po_file_path, "w", encoding="utf-8") as po_file:
                po_file.write("# Translations for " + self.base_name + "\n\n")

                # Iterate over English translations
                for key, english_text in english_parser.tra_translations.items():
                    french_text = french_parser.tra_translations.get(key, "")

                    po_file.write(f'msgctxt "{key}"\n')
                    po_file.write(f'msgid "{english_text}"\n')
                    po_file.write(f'msgstr "{french_text}"\n\n')
        except FileNotFoundError:
            print(f"Error: Could not create .po file: {self.po_file_path}")
            return
        except UnicodeEncodeError:
            print(f"Error: Unable to write to .po file: {self.po_file_path}")
            return

        print(f"Conversion to {self.po_file_path} completed successfully.")

    def po_to_tra(self):
        """Converts a .po file to a .tra file."""
        # Parse .po file
        po_parser = PoFileParser(self.po_file_path)
        po_parser.parse()

        # Check if po_translations is empty (file not found or other error)
        if not po_parser.po_translations:
            print(f"Error: .po file not found or empty: {self.po_file_path}")
            return

        # Create the .tra file (UTF-8 encoding by default)
        try:
            with open(self.tra_file_path, "w", encoding="utf-8") as tra_file:
                for key, french_text in po_parser.po_translations.items():
                    # Write each entry to the .tra file
                    tra_file.write(f"@{key} = ~{french_text}~\n")

            # Convert the .tra file content to Windows-1252 encoding
            with open(self.tra_file_path, "r", encoding="utf-8") as tra_file:
                french_content = tra_file.read()
            with open(self.tra_file_path, "w", encoding="windows-1252") as tra_file:
                tra_file.write(french_content)

        except FileNotFoundError:
            print(f"Error: Could not create .tra file: {self.tra_file_path}")
            return
        except UnicodeEncodeError:
            print(f"Error: Unable to write to .tra file: {self.tra_file_path}")
            return

        print(f"Conversion to {self.tra_file_path} completed successfully.")

        # Display index ranges (same as before)
        # ... (code for displaying index ranges remains the same) 


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py tra_to_po <base_name>")
        print("  python convert.py po_to_tra <base_name>")
        sys.exit(1)

    command = sys.argv[1]
    base_name = sys.argv[2]

    # Create directories if they don't exist
    os.makedirs("Finished_po", exist_ok=True)
    os.makedirs("Finished_tra", exist_ok=True)

    converter = Converter(base_name)

    if command == "tra_to_po":
        converter.tra_to_po()
    elif command == "po_to_tra":
        converter.po_to_tra()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()