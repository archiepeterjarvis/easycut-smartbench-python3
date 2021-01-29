import time
import csv, os

def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + str(message))

class Localization(object):

    dictionary = {}

    # use this for just getting user language, and if it's empty just assume english
    persistent_language_path = './sb_values/user_language.txt'
    complete_foreign_dictionary_path = './asmcnc/comms/foreign_dictionary.csv'
    fast_dictionary_path = './sb_values/fast_dictionary.txt'

    default_lang = 'English (GB)'
    lang = default_lang

    # want to test:
    # how fast is loading in from multi-language file vs two-language file (for start-up purposes)

    def __init__(self):

        if os.path.exists(self.fast_dictionary_path):
            self.load_language()
        else:
            self.load_in_new_language(self.lang)

    def load_language(self):
        # I hope this will work in the way I expect, but can't be sure until it's tested
        csv_reader = csv.DictReader(open(self.fast_dictionary_path, "r"), delimiter=',')
        self.dictionary = dict(csv_reader)

    def load_in_new_language(self, language):
        self.lang = language

        with open(self.complete_foreign_dictionary_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for lines in csv_reader:
                self.dictionary[str(lines[self.default_lang])] = str(lines[self.lang])

        self.save_fast_dictionary()

    def save_fast_dictionary(self):

        dialect = csv.excel
        dialect.delimiter = ','

        with open(self.fast_dictionary_path,  'w') as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=self.dictionary.keys(), dialect=dialect)
            dict_writer.writeheader()
            dict_writer.writerows(dict_list)

    supported_languages = ['English (GB)', 'Korean (KOR)', 'German (DE)', 'French (FR)', 'Italian (IT)']