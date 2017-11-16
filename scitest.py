from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn import datasets, metrics

import pandas as pd
import numpy as np 

iris = datasets.load_iris()
classifier = LogisticRegression()
classifier.fit(iris.data, iris.target)
score = metrics.accuracy_score(iris.target, classifier.predict(iris.data))

print("Accuracy: %f" % score)