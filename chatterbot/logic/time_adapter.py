from datetime import datetime
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from chatterbot.exceptions import OptionalDependencyImportError


class TimeLogicAdapter(LogicAdapter):
    """
    The TimeLogicAdapter returns the current time.

    :kwargs:
        * *positive* (``list``) --
          The time-related questions used to identify time questions.
          Defaults to a list of English sentences.
        * *negative* (``list``) --
          The non-time-related questions used to identify time questions.
          Defaults to a list of English sentences.
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        try:
            from nltk import NaiveBayesClassifier
        except ImportError:
            message = (
                'Unable to import "nltk".\n'
                'Please install "nltk" before using the TimeLogicAdapter:\n'
                'pip3 install nltk'
            )
            raise OptionalDependencyImportError(message)

        self.positive = kwargs.get('positive', [
            'Que horas são?',
            'Que horas são agora?',
            'Que hora é?',
            'Você tem as horas?'
        ])

        self.negative = kwargs.get('negative', [
            'É hora de ir dormir',
            'É hora de tomar banho',
            'É hora de parar',
            'É hora de comer',
            'É hora de beber água',
            'É hora de relaxar'
            'Que horas você vai?',
            'Que horas passa o ônibus?',
            'Que horas fecha o mercado?',
            'Que horas você vem?',
            'Que horas você vai?'
        ])

        labeled_data = (
            [
                (name, 0) for name in self.negative
            ] + [
                (name, 1) for name in self.positive
            ]
        )

        train_set = [
            (self.time_question_features(text), n) for (text, n) in labeled_data
        ]

        self.classifier = NaiveBayesClassifier.train(train_set)

    def time_question_features(self, text):
        """
        Provide an analysis of significant features in the string.
        """
        features = {}

        # A list of all words from the known sentences
        all_words = " ".join(self.positive + self.negative).split()

        # A list of the first word in each of the known sentence
        all_first_words = []
        for sentence in self.positive + self.negative:
            all_first_words.append(
                sentence.split(' ', 1)[0]
            )

        for word in text.split():
            features['first_word({})'.format(word)] = (word in all_first_words)

        for word in text.split():
            features['contains({})'.format(word)] = (word in all_words)

        for letter in 'abcdefghijklmnopqrstuvwxyz':
            features['count({})'.format(letter)] = text.lower().count(letter)
            features['has({})'.format(letter)] = (letter in text.lower())

        return features

    def process(self, statement, additional_response_selection_parameters=None):
        now = datetime.now()

        time_features = self.time_question_features(statement.text.lower())
        confidence = self.classifier.classify(time_features)
        response = Statement(text='Agora são ' + now.strftime('%H:%M'))

        response.confidence = confidence
        return response
