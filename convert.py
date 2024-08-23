import os
import re
import sys
import chardet


def escape_quotes(text):
    """Escape double quotes in the text."""
    return text.replace('"', r"\"")


def parse_tra_file(file_path, encoding="utf-8"):
    """Parses a .tra file and returns a dictionary with the index as key
    and the text as value."""
    tra_translations = {}
    try:
        with open(file_path, "r", encoding=encoding) as file:
            # Read the entire file content
            file_content = file.read()

            # Match all index lines and their text
            matches = re.findall(r"@(\d+)\s*=\s*~(.*?)~", file_content, re.DOTALL)
            for match in matches:
                tra_translations[match[0]] = escape_quotes(match[1])
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file {file_path} with encoding {encoding}")
    return tra_translations


def parse_po_file(file_path, encoding="utf-8"):
    """Parses a .po file and returns a dictionary with the msgctxt as key and msgstr as value."""
    po_translations = {}

    try:
        with open(file_path, "r", encoding=encoding) as file:
            # Read the entire file content
            file_content = file.read()

            # Match all msgctxt and msgstr lines using regex
            matches = re.findall(
                r'msgctxt "(.*?)"\s*msgid "(.*?)"\s*msgstr "(.*?)"',
                file_content,
                re.DOTALL,
            )
            for match in matches:
                current_key = match[0]
                msgstr = match[2].replace('\\"', '"').strip()
                po_translations[current_key] = msgstr

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file {file_path} with encoding {encoding}")

    return po_translations


def tra_to_po(base_name):
    """Converts a .tra file to a .po file."""
    # Define paths
    english_file_path = os.path.join("English", f"{base_name}.tra")
    french_file_path = os.path.join("French", f"{base_name}.tra")
    # Save to Finished_po directory
    po_file_path = os.path.join("Finished_po", f"{base_name}.po")

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
    except UnicodeDecodeError:
        print(f"Error: Unable to decode French file: {french_file_path}")
        return

    # Parse .tra files
    english_translations = parse_tra_file(english_file_path)
    french_translations = parse_tra_file(french_file_path, encoding="utf-8")

    # Create the .po file
    try:
        with open(po_file_path, "w", encoding="utf-8") as po_file:
            po_file.write("# Translations for " + base_name + "\n\n")

            # Iterate over English translations
            for key, english_text in english_translations.items():
                french_text = french_translations.get(key, "")

                po_file.write(f'msgctxt "{key}"\n')
                po_file.write(f'msgid "{english_text}"\n')
                po_file.write(f'msgstr "{french_text}"\n\n')
    except FileNotFoundError:
        print(f"Error: Could not create .po file: {po_file_path}")
        return
    except UnicodeEncodeError:
        print(f"Error: Unable to write to .po file: {po_file_path}")
        return

    print(f"Conversion to {po_file_path} completed successfully.")


def po_to_tra(base_name):
    """Converts a .po file to a .tra file."""
    # Define paths
    po_file_path = os.path.join("Finished_po", f"{base_name}.po")
    output_file = os.path.join("Finished_tra", f"{base_name}.tra")

    # Parse .po file
    po_translations = parse_po_file(po_file_path)

    # Check if po_translations is empty (file not found or other error)
    if not po_translations:
        print(f"Error: .po file not found or empty: {po_file_path}")
        return

    # Create the .tra file (UTF-8 encoding by default)
    try:
        with open(output_file, "w", encoding="utf-8") as tra_file:
            for key, french_text in po_translations.items():
                # Write each entry to the .tra file
                tra_file.write(f"@{key} = ~{french_text}~\n")

        # Convert the .tra file content to Windows-1252 encoding
        with open(output_file, "r", encoding="utf-8") as tra_file:
            french_content = tra_file.read()
        with open(output_file, "w", encoding="windows-1252") as tra_file:
            tra_file.write(french_content)

    except FileNotFoundError:
        print(f"Error: Could not create .tra file: {output_file}")
        return
    except UnicodeEncodeError:
        print(f"Error: Unable to write to .tra file: {output_file}")
        return

    print(f"Conversion to {output_file} completed successfully.")

    # Display index ranges
    index_ranges = []
    current_range_start = None
    previous_key = None

    for key in sorted(int(k) for k in po_translations.keys()):
        if current_range_start is None:
            # Start of a new range
            current_range_start = key
        elif previous_key is not None and key != previous_key + 1:
            # End of the current range, because keys are not consecutive
            if current_range_start == previous_key:
                # If the range contains only one index
                index_ranges.append(f"{current_range_start}")
            else:
                index_ranges.append(f"{current_range_start}-{previous_key}")
            # Start a new range
            current_range_start = key
        previous_key = key

    # Add the last range
    if current_range_start is not None:
        if current_range_start == previous_key:
            index_ranges.append(f"{current_range_start}")
        else:
            index_ranges.append(f"{current_range_start}-{previous_key}")

    # Display index ranges
    print("\nIndex ranges:")
    for range_str in index_ranges:
        print(range_str)


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

    # Create directories if they don't exist
    os.makedirs("Finished_po", exist_ok=True)
    os.makedirs("Finished_tra", exist_ok=True)

    if command == "tra_to_po":
        tra_to_po(base_name)
    elif command == "po_to_tra":
        po_to_tra(base_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()