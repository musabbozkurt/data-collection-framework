import os
import string

import numpy as np
from sklearn import cross_validation, svm
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB

from DM.TokenizationTweet import TokenizationTweet


class TermFrequency:
    def preprocess(term):
        return term.lower().translate(string.punctuation)

    # returns the distinct elements from a list
    def distinct(myList):
        seen = set()
        seen_add = seen.add
        return [x for x in myList if not (x in seen or seen_add(x))]

    def termfreq(fpath, numofFold, numofsplit, testSize, randomState, testSizeforTraintest, cforKernel):
        classLabels = []
        fileNames = []
        for subdir, dirs, files in os.walk(fpath):
            for file in files:
                file_path = subdir + os.path.sep + file
                fileNames.append(file_path)
                classLabels.append(subdir[15:])
        tfidf = TfidfVectorizer(tokenizer=TokenizationTweet.tokenize, preprocessor=TermFrequency.preprocess,
                                lowercase=True)
        # tfidf = TfidfVectorizer(tokenizer=TokenizationTextFile.tokenTextFile, preprocessor=TermFrequency.preprocess,lowercase=True)
        docTermMatrix = tfidf.fit_transform((open(f, encoding="ISO-8859-1").read() for f in fileNames))

        print(docTermMatrix.shape)
        print(classLabels)

        # test on training set
        X_train = docTermMatrix
        y_train = classLabels
        X_test = docTermMatrix
        y_test = classLabels

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        evalReport = classification_report(y_test, predictions,
                                           target_names=classifier.classes_)  # distinct(classLabels))
        print(evalReport)

        cm = confusion_matrix(classLabels, predictions)
        print("Confusion matrix:")
        print(cm)

        # train-test split 60%-40%
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(docTermMatrix, classLabels,
                                                                             test_size=testSizeforTraintest,
                                                                             random_state=randomState)

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        accuracy = classifier.score(X_test, y_test)
        print(accuracy)

        evalReport = classification_report(y_test, predictions, target_names=TermFrequency.distinct(classLabels))
        print(evalReport)

        cm = confusion_matrix(y_test, predictions)
        print("Confusion matrix:")
        print(cm)

        X = np.array(X_train)
        y = np.array(y_train)
        X2 = np.array(X_test)
        y2 = np.array(y_test)

        print(X.shape, y.shape, X2.shape, y2.shape)

        # support vector machines sklearn svc is one of the classfiers
        clf = svm.SVC(kernel='linear', C=cforKernel)
        scores = cross_val_score(clf, docTermMatrix, classLabels, cv=numofFold)
        print('scores : ', scores)

        mean_score = scores.mean()
        print('mean_score : ', mean_score)

        # calculation of  area under  curve
        std_dev = scores.std()
        std_error = scores.std() / np.math.sqrt(scores.shape[0])
        ci = 2.262 * std_error
        lower_bound = mean_score - ci
        upper_bound = mean_score + ci
        print("Score is %f +/-  %f" % (mean_score, ci))
        print(
            '95 percent probability that if this experiment were repeated over and over the average score would be between %f and %f' % (
            lower_bound, upper_bound))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        scores = cross_val_score(clf, docTermMatrix, classLabels, cv=numofFold, scoring='f1_macro')

        # test accuracy 1 0 arasi
        print('f1_macro scoring : ', scores)
        cv = ShuffleSplit(n_splits=numofsplit, test_size=testSize, random_state=randomState)

        print(cross_val_score(clf, docTermMatrix, classLabels, cv=cv))
        predicted = cross_val_predict(clf, docTermMatrix, classLabels, cv=numofFold)
        print(str(numofFold) + '-fold cross validation : ', metrics.accuracy_score(classLabels, predicted))
