import pandas as pd
import numpy as np
import re

import nltk
from nltk.stem import PorterStemmer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from operator import itemgetter

from parse.parser import get_data_from_db

if __name__ == '__main__':
    # Собираем данные из БД и складываем в дата фрейм
    data = get_data_from_db("topics.sqlite")
    df = pd.DataFrame([list(itemgetter(2, 7, )(i)) for i in data],
                      columns=['title', 'theme'])
    # Преобразование меток
    df['theme'] = np.where(
        np.logical_or(df['theme'] == 'Компьютерные и информационные науки', df['theme'] == 'Математика'), 1, 0)

    # Нижний регистр
    df['title'] = df['title'].str.lower()

    # Убираем знаки препинания
    p = re.compile(r'[^\w\s\d]+')
    df['title'] = [p.sub('', x) for x in df['title'].tolist()]

    # Токенизация
    df['title'] = df['title'].apply(nltk.word_tokenize)

    # Стемминг
    stemmer = PorterStemmer()
    df['title'] = df['title'].apply(lambda x: [stemmer.stem(y) for y in x])
    df['title'] = df['title'].apply(lambda x: ' '.join(x))

    print(df)

    # Преобразование для обучения модели
    count_vect = CountVectorizer()
    counts = count_vect.fit_transform(df['title'])

    transformer = TfidfTransformer().fit(counts)

    counts = transformer.transform(counts)

    X_train, X_test, y_train, y_test = train_test_split(counts, df['theme'], test_size=0.15, random_state=69)

    model = MultinomialNB().fit(X_train, y_train)
    predicted = model.predict(X_test)

    print(confusion_matrix(y_test, predicted))
    accuracy = accuracy_score(y_test, predicted)
    print("Accuracy   :", accuracy)
    precision = precision_score(y_test, predicted)
    print("Precision :", precision)
    recall = recall_score(y_test, predicted)
    print("Recall    :", recall)
    F1_score = f1_score(y_test, predicted)
    print("F1-score  :", F1_score)
