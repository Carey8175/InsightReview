import json
import csv


def jsonl_to_csv(jsonl_file, csv_file):
    """
    Convert a JSONL file to a CSV file.
    :param jsonl_file: Path to the input JSONL file.
    :param csv_file: Path to the output CSV file.
    """
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(csv_file, 'w', newline='',
                                                                 encoding='utf-8') as outfile:
        # Read the first line to get fieldnames
        first_line = json.loads(infile.readline().strip())
        fieldnames = list(first_line.keys())

        # Create CSV writer
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write first record
        writer.writerow(first_line)

        # Process the rest of the file
        for line in infile:
            writer.writerow(json.loads(line.strip()))


if __name__ == '__main__':
    import os

    file_names = os.listdir('./jsonl')
    for file_name in file_names:
        jsonl_to_csv(f'./jsonl/{file_name}', f'./csv/{file_name.replace(".jsonl", ".csv")}')
        print()