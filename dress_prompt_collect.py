import os
import re

def extract_section_from_files(directory, pattern, flags=re.DOTALL):
    extracted_data = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.txt'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(pattern, content, flags)
                    extracted_data[os.path.splitext(file)[0]] = matches if matches else None
    return extracted_data

def write_extracted_data_oneline(output_file, extracted_data, separator=' | '):
    with open(output_file, 'w', encoding='utf-8') as f:
        for filename, texts in extracted_data.items():
            if texts:
                joined_text = ' ; '.join(text.replace('\n', ' ').strip() for text in texts)
            else:
                joined_text = "None"
            f.write(f"{filename}{separator}{joined_text}\n")

# Directory containing your .txt files
directory = r"C:\Personal\Developed\Hailuio\prompt_images\New folder"

# Regex pattern to extract text inside double quotes
pattern = r'"(.*?)"'

# Extract and write
extracted_data = extract_section_from_files(directory, pattern)
output_file = r"Dresses.txt"
write_extracted_data_oneline(output_file, extracted_data)
