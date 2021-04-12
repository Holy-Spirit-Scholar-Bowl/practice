import csv
import json
import re

BASE_PATH = '/Users/alexhalbesleben/Documents/Programming/TypeScript projects/Scholar Bowl Analyzer/'
INPUT_FILE_PATH = BASE_PATH + 'database.json'

OUTPUT_FILE_PATH = BASE_PATH + 'database2.csv'

FIELDNAMES = ('category', 'subcategory', 'difficulty', 'tournament', 'question', 'source', 'num', 'year', 'answer', 'seen', 'type', 'round') # Change this to your field names

with open(INPUT_FILE_PATH) as fin, open(OUTPUT_FILE_PATH, 'w') as fout:

    writer = csv.DictWriter(fout, fieldnames=FIELDNAMES,)

    writer.writeheader()

    for line in fin:

        serialized_line = json.loads(line)
        if serialized_line['category'] == 'Literature' and serialized_line['difficulty'] == 'HS':
            extractedAnswer = re.match('\\{(.+?)\\}', serialized_line['answer'])
            if extractedAnswer:
                serialized_line['answer'] = extractedAnswer.group(1)
            else:
                serialized_line['answer'] = re.sub("\\s?\\[.*\\]\\s?", "", serialized_line['answer'])

            
            writer.writerow(serialized_line)