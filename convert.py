import os
import re
import sys

def escape_quotes(text):
    """
    Escape double quotes in the text.
    """
    return text.replace('"', r'\"')

def parse_tra_file(file_path, encoding='utf-8'):
    """
    Parse a .tra file and return a dictionary with the index as key and the text as value.
    """
    entries = {}
    with open(file_path, 'r', encoding=encoding) as file:
        # Read entire file content
        file_content = file.read()

        # Match all index lines and their text
        matches = re.findall(r'@(\d+)\s*=\s*~(.*?)~', file_content, re.DOTALL)
        for match in matches:
            entries[match[0]] = escape_quotes(match[1])

    return entries

def parse_po_file(file_path, encoding='utf-8'):
    """
    Parse a .po file and return a dictionary with the msgctxt as key and msgstr as value.
    """
    entries = {}
    with open(file_path, 'r', encoding=encoding) as file:
        current_key = None
        for line in file:
            line = line.strip()

            if line.startswith('msgctxt'):
                match = re.match(r'msgctxt "(.*)"', line)
                if match:
                    current_key = match.group(1)
                    entries[current_key] = {'msgid': '', 'msgstr': ''}
            elif line.startswith('msgid'):
                match = re.match(r'msgid "(.*)"', line)
                if match:
                    entries[current_key]['msgid'] = escape_quotes(match.group(1))
            elif line.startswith('msgstr'):
                match = re.match(r'msgstr "(.*)"', line)
                if match:
                    entries[current_key]['msgstr'] = escape_quotes(match.group(1))

    return entries

def tra_to_po(base_name):
    """
    Convert a .tra file to a .po file.
    """
    # Define paths
    english_file_path = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/English/{base_name}.tra'
    french_file_path = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/French/{base_name}.tra'
    # Save to Working_po directory
    po_working_file_path = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/Working_po/{base_name}.po'

    # Parse tra files
    english_translations = parse_tra_file(english_file_path)
    french_translations = parse_tra_file(french_file_path)

    # Create the .po file
    with open(po_working_file_path, 'w', encoding='utf-8') as po_file:
        po_file.write('# Translations for ' + base_name + '\n\n')
        
        # Iterate over the English translations
        for key, english_text in english_translations.items():
            french_text = french_translations.get(key, '')

            po_file.write(f'msgctxt "{key}"\n')
            po_file.write(f'msgid "{english_text}"\n')
            po_file.write(f'msgstr "{french_text}"\n\n')

    print(f"Conversion to {po_working_file_path} completed successfully.")

def po_to_tra(english_file_path, po_file_path, output_file):
    """
    Convert a .po file to a .tra file.
    """
    # Parse .po file
    po_translations = parse_po_file(po_file_path)
    english_translations = parse_tra_file(english_file_path)

    # Create the .tra file
    with open(output_file, 'w', encoding='utf-8') as tra_file:
        for key, value in english_translations.items():
            english_text = value
            french_text = po_translations.get(key, {}).get('msgstr', '')

            tra_file.write(f'@{key} = ~{escape_quotes(english_text)}~\n')
            tra_file.write(f'@{key} = ~{escape_quotes(french_text)}~\n')

    print(f"Conversion to {output_file} completed successfully.")

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python Tra.py tra_to_po <base_name>")
        print("  python Tra.py po_to_tra <base_name>")
        sys.exit(1)

    command = sys.argv[1]
    base_name = sys.argv[2]

    if command == 'tra_to_po':
        tra_to_po(base_name)
    elif command == 'po_to_tra':
        english_file_path = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/English/{base_name}.tra'
        # Use Finished_po directory for po_to_tra
        po_file_path = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/Finished_po/{base_name}.po'
        output_file = f'C:/Users/leilu/OneDrive/Prog/Trad_IWD2EE/tra/Finished_tra/{base_name}.tra'
        po_to_tra(english_file_path, po_file_path, output_file)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()