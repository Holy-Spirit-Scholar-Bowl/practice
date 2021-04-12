from json import loads
import json
from math import log
import os
import random
import re
from time import perf_counter
from re import sub, match
from string import punctuation
from typing import Counter
from nltk import word_tokenize, edit_distance
from nltk.collocations import BigramCollocationFinder,TrigramCollocationFinder,QuadgramCollocationFinder
from nltk.corpus import stopwords
from nltk.metrics.association import BigramAssocMeasures,TrigramAssocMeasures,QuadgramAssocMeasures
from hashlib import sha256

class Database:
    questions = []

	# All questions in the current database in certain categories (e.g. Literature, Fine Arts)
    def category(self, *args):
        return Database(list(filter(lambda question: question["category"] in args, self.questions)))

	# All questions in the current database with certain difficulties (e.g. HS, MS)
    def difficulty(self, *args):
        return Database(list(filter(lambda question: question["difficulty"] in args, self.questions)))

    # All questions in the current database with certain types (e.g. qb)
    def type(self, *args):
        return Database(list(filter(lambda question: question["type"] in args, self.questions)))

    # All questions in the current database with certain subcategories
    def subcategory(self, *args):
        return Database(list(filter(lambda question: question["subcategory"] in args, self.questions)))

    # Raw question-and-answer pairs from this database
    def rawQuestionsAndAnswers(self):
        return map(lambda q: (q["question"], q["answer"]), self.questions)

    # Formatted answer pairs
    def questionsAndAnswers(self):
        return map(lambda q: (q["question"], self.formatAnswer(q["answer"])), self.questions)

    # Whether two answers are close enough to be the same
    def answersSimilar(self, *args) -> bool:
        # These answers are close, but not the same
        notEqual = [("Dickens", "Dickinson"), ("Stowe", "Owen"), ("Odin", "Rodin"), ("Poe", "Stowe"), ("Poe", "Owen"), ("Mailer", "Miller")]
        if any(((args[0] == pair[0] and args[1] == pair[1]) or (args[1] == pair[0] and args[0] == pair[1])) for pair in notEqual):
            return False
        
        # If the Levenshtein distance is close enough, they are the same
        return edit_distance(args[0].lower(), args[1].lower(), substitution_cost=2.5) < (max(len(args[0]), len(args[1])) / 2)

    # All questions in the current database with a given answer
    def answer(self, answer):
        answerValid = lambda ans: self.answersSimilar(answer, self.formatAnswer(ans))
        return Database(list(filter(lambda question: answerValid(question["answer"]), self.questions)))

    # Returns collocations (common groups of words) in questions in this database with a given answer
    def collocationsWithAnswer(self, answer):
        questions = self.answer(answer) # Only use questions with the given answer
        # Treat the question as one big question
        joinedQuestions = " ".join(list(map(lambda q: q["question"], questions.questions))).lower()
        words = word_tokenize(joinedQuestions) # Split the question into words and puncutation

        stopwordFilter = lambda w: w in stopwords.words("english") # Take out common words
        punctuationFilter = lambda w: w in punctuation # Take out punctuation
        # Take out these common words
        customFilter = lambda w: w in ["10", "points", "name", "--", "ftp", ".", ",", ";", "?", "!", "'", "“", "”", "``", "''", "'s", "-", "’", "title", "character", "novel", "novella", "play", "poem", "whose", "author", "also", "wrote", "poems", ]
        wordFilter = lambda w: stopwordFilter(w) or punctuationFilter(w) or customFilter(w) # Combine the three filters above

        bi = BigramCollocationFinder.from_words(words) # Finds bigrams, groups of two words
        bi.apply_word_filter(wordFilter) # Use the filters above
        tri = TrigramCollocationFinder.from_words(words)
        tri.apply_word_filter(wordFilter)
        quad = QuadgramCollocationFinder.from_words(words)
        quad.apply_word_filter(wordFilter)

        # Score each bigram, trigram, and quadgram
        bigram = bi.score_ngrams(BigramAssocMeasures.likelihood_ratio)
        trigram = tri.score_ngrams(TrigramAssocMeasures.likelihood_ratio)
        quadgram = quad.score_ngrams(QuadgramAssocMeasures.likelihood_ratio)

        # Quadgrams are weighted a little bit more than trigrams, which are weighted slightly more than bigrams, etc.
        weightFn = lambda x: log(x/10 + 1)
        # Adjust each score by the weight
        ngramFn = lambda ngram: (ngram[0], ngram[1] * weightFn(len(ngram[0])))

        # Combine the bigrams, trigrams, and quadgrams
        ngrams = list(map(ngramFn, bigram + trigram + quadgram))
        # Sort by weighted score
        ngrams.sort(key=lambda ngram: ngram[1], reverse=True)
        # Take out the score and return the sorted list
        return list(map(lambda ngram: ngram[0], ngrams))


    # Formats a raw answer into the pure answer
    def formatAnswer(self, ans):
        # Take out text in brackets and parentheses
        answer = sub("[\\[\\(].*?[\\]\\)]", "", ans)
        # If text in brackets, use that text
        brackets = match("\\{(.+)\\}", answer)
        # If there is no text in brackets, use the entire answer
        answer = brackets.group(1) if brackets else answer
        # Take out any brackets remaining and strip off leading and trailing spaces
        return sub("[\\}\\{]", "", answer).strip()

    def getID(self):
        hash = sha256()
        for question in self.questions:
            hash.update(question["answer"].encode("utf-8"))
        
        return hash.hexdigest()

    # Sort questions by their answerr]
    def answerSort(self):
        id = str(self.getID())

        frequencyListsGenerated = os.listdir("Frequency Lists")
        if (id + ".json") in frequencyListsGenerated:
            with open("Frequency Lists/" + id + ".json", encoding="utf-8") as f:
                return json.load(f)

        answers = {}
        questions = self.questions.copy()

        # To display a progress bar
        startTime = perf_counter()
        originalLength = len(questions)

        # Iterates over questions
        while len(questions) > 0:
            q = questions[0]

            # Go ahead and format the answer
            q["answer"] = self.formatAnswer(q["answer"])

            # If the answer has been stored
            keyExists = lambda ans: self.answersSimilar(q["answer"], ans)
            # Where the answer is located
            key = next((ans for ans in answers.keys() if keyExists(ans)), q["answer"])
            
            # Add the question to the list of questions for its answer
            answers[key] = answers.get(key, []) + [q["question"]]

            # Remove the question so we don't deal with it again
            questions.pop(0)

            # Progress bar stuff
            currentTime = perf_counter()
            numQuestions = len(questions)
            percentFinished = 100 - (numQuestions/originalLength) * 100
            elapsedTime = currentTime-startTime
            eta = elapsedTime / (percentFinished / 100) - elapsedTime
            print("\r{}/{} questions ({:.2f}%). {:.2f} seconds elapsed, ETA {:.2f}s.\t\t".format(originalLength - numQuestions, originalLength, percentFinished, elapsedTime, eta), end="")

        with open(os.path.join("Frequency Lists", id + ".json"), "w+") as f:
            f.write(json.dumps(answers))

        print()
        
        return answers

    # Format a group of words as a string
    def collocationTupleAsString(self, collocation):
        return ' '.join(collocation).strip()

    def generateSets(self, questions=None, maxSets=1000, perSet=20, inFolder="questions", filenameRoot="set"):
        if questions is None:
            questions = self.questions.copy()
        random.shuffle(questions)

        if not os.path.exists(inFolder):
            os.mkdir(inFolder)
        
        for i in range(0, maxSets):
            filename = inFolder + "/" + filenameRoot + str(i + 1) + ".html"
            file = open(filename, "w+")

            for j in range(0, perSet):
                try:
                    question = questions.pop(0)
                except IndexError:
                    file.close()
                    return
                
                line1 = str(j + 1) + ". " + question["category"] + "/" + (question["subcategory"] or "All") + " (" + question["tournament"] + " " +  str(question["year"]) + ")<br>"
                line2 = re.sub(r"(^.*)\(\*\)", r"<strong>\1</strong>", question["question"]) + "<br>"
                line3 = "ANSWER: " + re.sub(r"\{(.+?)\}", r"<u>\1</u>", question["answer"]) + "<br><br>"

                file.write(line1 + line2 + line3)

            file.close()
            

    def generateSetWithWeights(self, setLength = 20, art=12, geography=3, history=23, literature=22, mythology=4, philosophy=3, religion=3, science=19, socialScience=5, trash=5):
        choices = ["Fine Arts", "Geography", "History", "Literature", "Mythology", "Philosophy", "Religion", "Science", "Social Science", "Trash"]
        weights = [art, geography, history, literature, mythology, philosophy, religion, science, socialScience, trash]
        categories = random.choices(choices, weights=weights, k=setLength)
        instances = Counter(categories)

        questionSet = []

        for cat in choices:
            for num in range(0, instances.get(cat) or 0):
                questionSet.append(self.category(cat).questions[num])

        return questionSet

    def __init__(self, data) -> None:
        self.questions = data

db = Database(list(loads(line) for line in open('database.json')))

for cat in ["Mythology", "Philosophy", "Social Science", "Trash", "Religion", "Geography", "Fine Arts", "Literature", "Science", "History"]:
    print(cat)
    db.difficulty("HS").category(cat).answerSort()