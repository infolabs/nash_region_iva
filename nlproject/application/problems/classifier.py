from math import log
from datetime import datetime
from operator import itemgetter

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer
from nltk.cluster.util import cosine_distance


class Filter:
    pre_stemming = []
    pre_stemming.extend(stopwords.words('russian'))
    pre_stemming.extend([c for c in '!?.,:()<>-;&«»№–'])
    pre_stemming.extend(
        ["''", "``", 'quot', '...', 'laquo', 'raquo', 'p', '/p']
    )
    post_stemming = [
        'котор', 'сво', 'дан', 'эт', 'наш', 'год', 'прош', 'так',
        'сво', 'мо', 'очен', 'просьб', 'сдела', 'г.', 'должн', 'наход',
        'нам', 'здравств', 'добр', 'хот', 'никак', 'никт', 'спасиб',
        'стал', 'ул', 'вопрос', 'белгородск', 'ответ', 'такж', 'все',
        'пробл', 'вообщ', 'необходим', 'ук', 'проблем', 'возл', 'написа'
    ]


class Classifier:
    def __init__(self):
        self.words = set()
        self.problems = {}
        self.appearances = {}

        self.filter = Filter()
        self.stemmer = RussianStemmer()

    @staticmethod
    def tfidf(words, words_count, categories_count, appearances_mapping):
        tfidfs = {}
        for word in set(words):
            tf = words.count(word) / words_count
            idf = log(categories_count / appearances_mapping[word])
            tfidfs[word] = tf * idf
        return tfidfs

    @staticmethod
    def tokenize(text, stemmer, pre_stemming_filter, post_stemming_filter):
        words = []
        for word in word_tokenize(text.lower()):
            if word in pre_stemming_filter:
                continue
            word = stemmer.stem(word)
            if word in post_stemming_filter:
                continue
            words.append(word)
        return words

    def load_problems(self):
        with open('problems/new-clean.txt', 'r') as f:
            content = f.read()
            content = content.replace('L,', ',')
            content = content.replace('L]', ']')
            content = content.replace('L}', '}')
            problems = eval(content)

        for problem in problems:
            if not problem['text']:
                continue

            index = problem['typical_problem_id']
            if not self.problems.get(index):
                self.problems[index] = {
                    'id': problem['typical_problem_id'],
                    'name': problem['typical_problem_text'],
                    'problems': [],
                }

            self.problems[index]['problems'].append(
                {
                    'id': problem['id'],
                    'text': problem['text'],
                }
            )

    def process_problems(self):
        for index, typical_problem in self.problems.items():
            typical_problem['words'] = []

            for particular_problem in typical_problem['problems']:
                text = particular_problem['text']
                text += ' ' + typical_problem['name']
                particular_problem['words'] = self.tokenize(
                    text,
                    self.stemmer,
                    self.filter.pre_stemming,
                    self.filter.post_stemming,
                )
                particular_problem['count'] = len(particular_problem['words'])
                typical_problem['words'].extend(particular_problem['words'])

            typical_problem['count'] = len(typical_problem['words'])

            typical_problem_words_set = set(typical_problem['words'])
            self.words = self.words.union(typical_problem_words_set)
            for word in typical_problem_words_set:
                self.appearances[word] = self.appearances.get(word, 0) + 1

        self.problems_count = len(self.problems)
        for index, typical_problem in self.problems.items():
            typical_problem['tfidf'] = self.tfidf(
                typical_problem['words'],
                typical_problem['count'],
                self.problems_count,
                self.appearances,
            )
            typical_problem['vector'] = [
                typical_problem['tfidf'].get(word, 0.0)
                for word in self.words
            ]

    def classify(self, text):
        now = datetime.now()
        words = self.tokenize(
            text,
            self.stemmer,
            self.filter.pre_stemming,
            self.filter.post_stemming,
        )

        appearances = self.appearances.copy()
        for word in set(words):
            appearances[word] = appearances.get(word, 0) + 1

        tfidfs = self.tfidf(
            words,
            len(words),
            self.problems_count,
            appearances
        )
        vector = [
            tfidfs[word] if word in tfidfs else 0.0
            for word in self.words
        ]

        distances = []
        for index, typical_problem in self.problems.items():
            distance = cosine_distance(vector, typical_problem['vector'])
            distances.append(
                {
                    'id': typical_problem['id'],
                    'name': typical_problem['name'],
                    'distance': distance
                }
            )

        distances.sort(key=itemgetter('distance'))
        print('Estimated:', datetime.now() - now)
        return distances
