import os
import re
import sys
import chardet
import json
import codecs


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
                tra_translations[match[0]] = match[1]
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except UnicodeDecodeError:
        # Get the detected encoding
        with open(file_path, "rb") as file:
            detected_encoding = chardet.detect(file.read())["encoding"]
        print(
            f"Error: Unable to decode file {file_path} with encoding {encoding}. "
            f"Detected encoding is: {detected_encoding}"
        )
    return tra_translations


def tra_to_json(base_name):
    """Converts a .tra file to a JSON file."""
    # Define paths
    english_file_path = os.path.join("English", f"{base_name}.tra")
    french_file_path = os.path.join("French", f"{base_name}.tra")
    # Save to Finished_json directory
    json_file_path = os.path.join("Finished_json", f"{base_name}.json")

    # Detect and convert French file encoding if needed
    try:
        with open(french_file_path, "rb") as french_file:
            french_content = french_file.read()
            encoding = chardet.detect(french_content)["encoding"]
            if encoding != "utf-8":
                print(f"Converting {french_file_path} from {encoding} to UTF-8...")
                with codecs.open(
                    french_file_path, "r", encoding=encoding
                ) as french_file:
                    french_content = french_file.read()
                with codecs.open(
                    french_file_path, "w", encoding="utf-8"
                ) as french_file:
                    french_file.write(french_content)
    except FileNotFoundError:
        print(f"Error: French file not found: {french_file_path}")
        return
    except UnicodeDecodeError:
        print(f"Error: Unable to decode French file: {french_file_path}")
        return

    # Parse .tra files
    english_translations = parse_tra_file(english_file_path)
    # Now parse the French file with utf-8 encoding
    french_translations = parse_tra_file(french_file_path, encoding="utf-8")

    # Create the JSON file
    try:
        translations = {}
        for key, english_text in english_translations.items():
            french_text = french_translations.get(key, "")
            # Replace single quotes with apostrophes in French text
            french_text = french_text.replace("'", "’")
            # Restore the correct structure of the dictionary
            translations[key] = {english_text: french_text}

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(translations, json_file, indent=4, ensure_ascii=False)

    except FileNotFoundError:
        print(f"Error: Could not create .json file: {json_file_path}")
        return
    except UnicodeEncodeError:
        print(f"Error: Unable to write to .json file: {json_file_path}")
        return

    print(f"Conversion to {json_file_path} completed successfully.")


def json_to_tra(base_name):
    """Converts a JSON file to a .tra file."""
    # Define paths
    json_file_path = os.path.join("Finished_json", f"{base_name}.json")
    english_file_path = os.path.join("English", f"{base_name}.tra")
    output_file = os.path.join("Finished_tra", f"{base_name}.tra")

    try:
        # Load the JSON file and replace single quotes with apostrophes
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            translations = json.load(json_file)

            # Replace single quotes with apostrophes in French text
            for key, value in translations.items():
                french_text = list(value.values())[0]  # Get the French text value
                french_text = french_text.replace("'", "’")  # Replace single quotes
                value[list(value.keys())[0]] = french_text  # Update the value in the dictionary

        # Create the .tra file (UTF-8 encoding by default)
        with open(output_file, "w", encoding="utf-8") as tra_file:
            for key, value in translations.items():
                # Extract the French text using a regex
                match = re.search(r": '(.*?)'", str(value))
                if match:
                    french_text = match.group(1)
                    # Replace escaped characters with actual characters
                    french_text = (
                        french_text.replace("\\n", "\n")
                        .replace("\\t", "\t")
                        .replace("\\xa0", " ")
                    )
                    # Write each entry to the .tra file
                    tra_file.write(f"@{key} = ~{french_text}~\n")
                else:
                    print(
                        f"Warning: Could not find French text for index {key} in {json_file_path}"
                    )

        # Convert the .tra file content to Windows-1252 encoding
        with open(output_file, "r", encoding="utf-8") as tra_file:
            french_content = tra_file.read()
        with open(output_file, "w", encoding="windows-1252") as tra_file:
            tra_file.write(french_content)

    except FileNotFoundError:
        print(f"Error: Could not find .json file: {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {json_file_path}")
        return
    except UnicodeEncodeError:
        print(f"Error: Unable to write to .tra file: {output_file}")
        return

    print(f"Conversion to {output_file} completed successfully.")

    # Display index ranges
    print("\nEnglish file index ranges:")
    display_index_ranges(english_file_path)
    print("\nTranslated file index ranges:")
    display_index_ranges(output_file)  # Pass the output_file path


def display_index_ranges(file_path):
    """Display index ranges from a .tra file and returns the ranges."""
    index_ranges = []
    current_range_start = None
    previous_key = None
    empty_ranges = []  # Nouvelle liste pour les plages d'index vides
    current_empty_range_start = None

    encoding = "windows-1252"  # Default encoding
    if "English" in file_path:
        encoding = "utf-8"

    try:
        with open(file_path, "r", encoding=encoding) as tra_file:
            file_content = tra_file.read()
            matches = re.findall(r"@(\d+)\s*=\s*~(.*?)~", file_content, re.DOTALL)

            for match in matches:
                key = int(match[0])

                # Vérification si le texte entre les ~ est vide
                if match[1].strip() == "":
                    if current_empty_range_start is None:
                        current_empty_range_start = key
                    elif previous_key is not None and key != previous_key + 1:
                        if current_empty_range_start == previous_key:
                            empty_ranges.append(f"{current_empty_range_start}")
                        else:
                            empty_ranges.append(
                                f"{current_empty_range_start}-{previous_key}"
                            )
                        current_empty_range_start = key
                    previous_key = key
                else:
                    # Si on rencontre un index non vide, on met à jour les ranges non vides
                    if current_range_start is None:
                        current_range_start = key
                    elif previous_key is not None and key != previous_key + 1:
                        if current_range_start == previous_key:
                            index_ranges.append(f"{current_range_start}")
                        else:
                            index_ranges.append(f"{current_range_start}-{previous_key}")
                        current_range_start = key
                    previous_key = key

                    # Si on rencontre un index non vide, on reset le range vide
                    current_empty_range_start = None

        # Add the last range
        if current_range_start is not None:
            if current_range_start == previous_key:
                index_ranges.append(f"{current_range_start}")
            else:
                index_ranges.append(f"{current_range_start}-{previous_key}")

        # Add the last empty range
        if current_empty_range_start is not None:
            if current_empty_range_start == previous_key:
                empty_ranges.append(f"{current_empty_range_start}")
            else:
                empty_ranges.append(f"{current_empty_range_start}-{previous_key}")

        # Display index ranges
        for range_str in index_ranges:
            print(range_str)

        # Display empty index ranges
        if empty_ranges:
            print("Index ranges with empty translations:")
            for range_str in empty_ranges:
                print(range_str)
            
    except FileNotFoundError:
        print(f"Error: Could not find .tra file: {file_path}")
        return

    return index_ranges


def compare_index_ranges(file_path1, file_path2):
    """Compares index ranges from two .tra files."""
    ranges1 = display_index_ranges(file_path1)
    ranges2 = display_index_ranges(file_path2)

    # Check for missing ranges in file2 compared to file1
    missing_ranges = [range_str for range_str in ranges1 if range_str not in ranges2]
    if missing_ranges:
        print(f"\nMissing index ranges in {file_path2} compared to {file_path1}:")
        for range_str in missing_ranges:
            print(range_str)
    else:
        print(f"\nNo missing index ranges in {file_path2} compared to {file_path1}")

    # Check for extra ranges in file2 compared to file1
    extra_ranges = [range_str for range_str in ranges2 if range_str not in ranges1]
    if extra_ranges:
        print(f"\nExtra index ranges in {file_path2} compared to {file_path1}:")
        for range_str in extra_ranges:
            print(range_str)
    else:
        print(f"\nNo extra index ranges in {file_path2} compared to {file_path1}")


# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python convert.py tra_to_json <base_name>")
        print("  python convert.py json_to_tra <base_name>")
        sys.exit(1)

    command = sys.argv[1]
    base_name = sys.argv[2]

    # Create directories if they don't exist
    os.makedirs("Finished_json", exist_ok=True)
    os.makedirs("Finished_tra", exist_ok=True)

    if command == "tra_to_json":
        tra_to_json(base_name)
    elif command == "json_to_tra":
        json_to_tra(base_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
