import pandas as pd
import itertools

class KeywordCombinations:
    def __init__(self, csv_file, output_file="search_words.txt"):
        self.keys_df = pd.read_csv(csv_file)
        self.keys_df.fillna(" ", inplace=True)
        self.output_file = output_file

    def get_columns_data(self):
        return [self.keys_df[col].to_list() for col in self.keys_df.columns]

    def create_combinations(self):
        columns_data = self.get_columns_data()
        combinations = list(itertools.product(*columns_data))
        search_word_list = [" ".join(map(str, combination)).strip() for combination in combinations]
        return search_word_list
    
    def word_count(self, text):
        return len(text.split())

    def get_unique_combinations(self):
        search_word_list = self.create_combinations()
        filtered_search_word_list = [word.lower() for word in search_word_list if self.word_count(word) > 1]
        unique_search_word_list = list(set(filtered_search_word_list))
        self.save_unique_combinations_text(unique_search_word_list)
        return unique_search_word_list

    def save_unique_combinations_text(self, unique_combinations):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for combination in unique_combinations:
                f.write(combination + '\n')
        print(f"Unique combinations saved to {self.output_file}")

    @staticmethod
    def read_from_text(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                combinations = [line.strip() for line in f.readlines()]
            print(f"Combinations read from {file}")
            return combinations
        except FileNotFoundError:
            print(f"File {file} not found.")
            return []

    @staticmethod
    def generate_and_save_combinations(csv_file, output_file="search_words.txt"):
        keyword_combinations = KeywordCombinations(csv_file, output_file)
        return keyword_combinations.get_unique_combinations()

