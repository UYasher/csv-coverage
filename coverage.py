import pandas as pd
from fuzzywuzzy import fuzz
import argparse

parser = argparse.ArgumentParser(description='Do coverage analysis for keywords')
parser.add_argument('keyword_file', type=str, help='A file containing keywords')
parser.add_argument('data_file', type=str, help='A file containing questions and answers')
args = parser.parse_args()

keyword_df = pd.read_csv(args.keyword_file)
keywords = keyword_df.words.unique()
data = pd.read_csv(args.data_file)


def percent_question_using_keywords():
    def match_funcs(keywords):
        return {
            "exact": lambda q: any(word in q.split(" ") for word in keywords),
            "lev": lambda q: any(fuzz.ratio(q, word) > 70 for word in keywords),
            "partial": lambda q: any(fuzz.partial_ratio(q, word) > 70 for word in keywords),
            "set": lambda q: any(fuzz.token_set_ratio(q, word) > 70 for word in keywords),
        }

    match_types = match_funcs([]).keys()

    def compute_coverage(keywords, data, match_type="exact"):
        f = match_funcs(keywords)[match_type]

        q_mask = data['Question'].apply(f)
        a_mask = data['Answer'].apply(f)
        qa_mask = q_mask | a_mask

        return tuple(len(data[mask])/len(data) for mask in [q_mask, a_mask, qa_mask])

    for match_type in match_types:
        print(compute_coverage(keywords, data, match_type))


def percent_keywords_used_in_questions():
    def match_funcs(series):
        return {
            "exact": lambda keyword: series.apply(lambda q: keyword in q).any(),
            # "lev": lambda keyword: series.apply(lambda q: fuzz.ratio(q, keyword) > 70).any(),
            # "partial": lambda keyword: series.apply(lambda q: fuzz.partial_ratio(q, keyword) > 70).any(),
            "set": lambda keyword: series.apply(lambda q: fuzz.token_set_ratio(q, keyword) > 0.70).any()
        }

    match_types = match_funcs([]).keys()

    def compute_coverage(keywords, data, match_type="exact"):
        fq = match_funcs(data['Question'])[match_type]
        fa = match_funcs(data['Answer'])[match_type]

        q_mask = keywords['words'].apply(fq)
        a_mask = keywords['words'].apply(fa)
        qa_mask = q_mask | a_mask

        return tuple(len(keywords[mask]) / len(keywords) for mask in [q_mask, a_mask, qa_mask])

    for match_type in match_types:
        print(compute_coverage(keyword_df, data, match_type))


# percent_question_using_keywords()
percent_keywords_used_in_questions()
