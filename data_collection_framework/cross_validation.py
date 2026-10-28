import math
import string
from pathlib import Path

from sklearn import metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from data_collection_framework.nlp import tokenization


class TermFrequency:
    @staticmethod
    def preprocess(term):
        return term.lower().translate(string.punctuation)

    @staticmethod
    def distinct(items):
        """Distinct elements of a list, keeping the original order."""
        return list(dict.fromkeys(items))

    @staticmethod
    def load_corpus(root):
        """Returns (file paths, class labels); the label is the name of the sub folder of each file."""
        file_names, class_labels = [], []
        for path in sorted(Path(root).rglob("*")):
            if path.is_file():
                file_names.append(path)
                class_labels.append(path.parent.name)
        return file_names, class_labels

    @staticmethod
    def termfreq(path, folds, splits, test_size, random_state, train_test_size, svm_c):
        file_names, class_labels = TermFrequency.load_corpus(path)
        tfidf = TfidfVectorizer(tokenizer=tokenization.tokenize, preprocessor=TermFrequency.preprocess,
                                lowercase=True)
        doc_term_matrix = tfidf.fit_transform((f.read_text(encoding="ISO-8859-1") for f in file_names))

        print(doc_term_matrix.shape)
        print(class_labels)

        # test on training set
        X_train = doc_term_matrix
        y_train = class_labels
        X_test = doc_term_matrix
        y_test = class_labels

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        eval_report = classification_report(y_test, predictions,
                                            target_names=classifier.classes_)  # distinct(class_labels))
        print(eval_report)

        cm = confusion_matrix(class_labels, predictions)
        print("Confusion matrix:")
        print(cm)

        # train-test split 60%-40%
        X_train, X_test, y_train, y_test = train_test_split(doc_term_matrix,
                                                            class_labels,
                                                            test_size=train_test_size,
                                                            random_state=random_state)

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        accuracy = classifier.score(X_test, y_test)
        print(accuracy)

        eval_report = classification_report(y_test, predictions, target_names=TermFrequency.distinct(class_labels))
        print(eval_report)

        cm = confusion_matrix(y_test, predictions)
        print("Confusion matrix:")
        print(cm)

        print(X_train.shape, len(y_train), X_test.shape, len(y_test))

        # support vector machines sklearn svc is one of the classfiers
        clf = svm.SVC(kernel='linear', C=svm_c)
        scores = cross_val_score(clf, doc_term_matrix, class_labels, cv=folds)
        print('scores : ', scores)

        mean_score = scores.mean()
        print('mean_score : ', mean_score)

        # calculation of  area under  curve
        std_error = scores.std() / math.sqrt(scores.shape[0])
        ci = 2.262 * std_error
        lower_bound = mean_score - ci
        upper_bound = mean_score + ci
        print("Score is %f +/-  %f" % (mean_score, ci))
        print(
            '95 percent probability that if this experiment were repeated over and over the average score would be between %f and %f' % (
                lower_bound, upper_bound))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        scores = cross_val_score(clf, doc_term_matrix, class_labels, cv=folds, scoring='f1_macro')

        # test accuracy 1 0 arasi
        print('f1_macro scoring : ', scores)
        cv = ShuffleSplit(n_splits=splits, test_size=test_size, random_state=random_state)

        print(cross_val_score(clf, doc_term_matrix, class_labels, cv=cv))
        predicted = cross_val_predict(clf, doc_term_matrix, class_labels, cv=folds)
        print(str(folds) + '-fold cross validation : ', metrics.accuracy_score(class_labels, predicted))


def evaluate(texts, labels, folds, splits, test_size, random_state, train_test_size, svm_c):
    """Cross validation of a text classifier that guesses which profile wrote a tweet; returns plain data."""
    from collections import Counter

    sizes = Counter(labels)
    usable = {label for label, count in sizes.items() if count >= folds}
    if len(usable) < 2:
        raise ValueError(f"Need at least 2 profiles with {folds}+ tweets each (have "
                         f"{', '.join(f'@{k}: {v}' for k, v in sizes.most_common()) or 'none'}).")
    pairs = [(t, label) for t, label in zip(texts, labels) if label in usable]
    texts, labels = [p[0] for p in pairs], [p[1] for p in pairs]
    matrix = TfidfVectorizer(lowercase=True).fit_transform(texts)
    classes = sorted(usable)

    X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=train_test_size,
                                                        random_state=random_state, stratify=labels)
    bayes = MultinomialNB().fit(X_train, y_train)
    clf = svm.SVC(kernel="linear", C=svm_c)
    accuracy = cross_val_score(clf, matrix, labels, cv=folds)
    f1_macro = cross_val_score(clf, matrix, labels, cv=folds, scoring="f1_macro")
    shuffle = cross_val_score(clf, matrix, labels, cv=ShuffleSplit(n_splits=splits, test_size=test_size,
                                                                   random_state=random_state))
    predicted = cross_val_predict(clf, matrix, labels, cv=folds)
    margin = 2.262 * accuracy.std() / math.sqrt(len(accuracy))  # t value for 95 % with 10 folds
    return {
        "documents": len(texts), "features": matrix.shape[1], "classes": classes,
        "class_sizes": {label: sizes[label] for label in classes},
        "holdout_accuracy": float(bayes.score(X_test, y_test)),
        "accuracy_scores": [float(x) for x in accuracy], "f1_macro_scores": [float(x) for x in f1_macro],
        "shuffle_scores": [float(x) for x in shuffle],
        "mean_accuracy": float(accuracy.mean()), "mean_f1_macro": float(f1_macro.mean()),
        "confidence_margin": float(margin),
        "cross_val_predict_accuracy": float(metrics.accuracy_score(labels, predicted)),
        "confusion_matrix": confusion_matrix(labels, predicted, labels=classes).tolist(),
    }
