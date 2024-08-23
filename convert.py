import os
import re
import sys
import chardet

# -----------------------------------------------------------------------------
# Escape and parsing functions
# -----------------------------------------------------------------------------

def escape_quotes(text):
    """Escape double quotes in the text."""
    return text.replace('"', r"\"")

def parse_tra_file(file_path, encoding="utf-8"):
    """Parses a .tra file and returns a dictionary with the index as key
    and the text as value."""
    tra_translations = {}
    with open(file_path, "r", encoding=encoding) as file:
        # Read the entire file content
        file_content = file.read()

        # Match all index lines and their text
        matches = re.findall(r"@(\d+)\s*=\s*~(.*?)~", file_content, re.DOTALL)
        for match in matches:
            tra_translations[match[0]] = escape_quotes(match[1])

    return tra_translations

def parse_po_file(file_path, encoding="utf-8"):
    """Parses a .po file and returns a dictionary with the msgctxt as key
    and msgstr as value."""
    po_translations = {}
    with open(file_path, "r", encoding=encoding) as file:
        current_key = None
        for line in file:
            line = line.strip()

            if "msgctxt" in line:
                match = re.match(r'msgctxt "(.*)"', line)
                if match:
                    current_key = match.group(1)
                    po_translations[current_key] = {"msgid": "", "msgstr": ""}
            elif "msgid" in line:
                match = re.match(r'msgid "(.*)"', line)
                if match:
                    # Do not escape if already escaped
                    po_translations[current_key]["msgid"] = match.group(1).replace('\\"', '"')
            elif "msgstr" in line:
                match = re.match(r'msgstr "(.*)"', line)
                if match:
                    # Do not escape if already escaped
                    po_translations[current_key]["msgstr"] = match.group(1).replace('\\"', '"')

    return po_translations

# -----------------------------------------------------------------------------
# Conversion functions
# -----------------------------------------------------------------------------

def tra_to_po(base_name):
    """Converts a .tra file to a .po file."""
    # Define paths
    english_file_path = f"./English/{base_name}.tra"
    french_file_path = f"./French/{base_name}.tra"
    # Save to Finished_po directory
    po_file_path = f"./Finished_po/{base_name}.po"

    # Detect and convert French file encoding if needed
    try:
        with open(french_file_path, "rb") as french_file:
            french_content = french_file.read()
            encoding = chardet.detect(french_content)["encoding"]
            if encoding != "utf-8":
                print(f"Converting {french_file_path} from {encoding} to UTF-8...")
                with open(french_file_path, "r", encoding=encoding) as french_file:
                    french_content = french_file.read()
                with open(french_file_path, "w", encoding="utf-8") as french_file:
                    french_file.write(french_content)
    except FileNotFoundError:
        print(f"Error: French file not found: {french_file_path}")
        return

    # Parse .tra files
    english_translations = parse_tra_file(english_file_path)
    french_translations = parse_tra_file(french_file_path, encoding="utf-8")

    # Create the .po file
    with open(po_file_path, "w", encoding="utf-8") as po_file:
        po_file.write("# Translations for " + base_name + "\n\n")

        # Iterate over English translations
        for key, english_text in english_translations.items():
            french_text = french_translations.get(key, "")

            po_file.write(f'msgctxt "{key}"\n')
            po_file.write(f'msgid "{english_text}"\n')
            po_file.write(f'msgstr "{french_text}"\n\n')

    print(f"Conversion to {po_file_path} completed successfully.")

def po_to_tra(base_name):
    """Converts a .po file to a .tra file."""
    # Define paths
    po_file_path = f"./Finished_po/{base_name}.po"
    output_file = f"./Finished_tra/{base_name}.tra"

    # Parse .po file
    po_translations = parse_po_file(po_file_path)

    # Create the .tra file (UTF-8 encoding by default)
    with open(output_file, "w", encoding="utf-8") as tra_file:
        for key, value in po_translations.items():
            french_text = value.get("msgstr", "")

            # Remove unnecessary escaping
            tra_file.write(f"@{key} = ~{french_text}~\n")  

    # Convert to Windows-1252
    with open(output_file, "r", encoding="utf-8") as tra_file:
        french_content = tra_file.read()
    with open(output_file, "w", encoding="windows-1252") as tra_file:
        tra_file.write(french_content)

    print(f"Conversion to {output_file} completed successfully.")

# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py tra_to_po <base_name>")
        print("  python convert.py po_to_tra <base_name>")
        sys.exit(1)

    command = sys.argv[1]
    base_name = sys.argv[2]

    if command == "tra_to_po":
        tra_to_po(base_name)
    elif command == "po_to_tra":
        po_to_tra(base_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()