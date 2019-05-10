#!/usr/bin/env python
# coding: utf-8

# # Import Libraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


from sklearn.preprocessing import MinMaxScaler, label_binarize, LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import LinearSVC, SVC
from sklearn.neighbors import NearestNeighbors, KDTree
from sklearn import neighbors

## Support Vector Classifier

def svm_classifier(X, y):
    clf = SVC(kernel='rbf', decision_function_shape='ovr', gamma='auto')
    clf.fit(X, y)

    return clf

## K-Nearest Neighbors Classifier

def nn_classifier(X, y, k=6):
#   print(y.shape)
    neighbor = k
    clf = neighbors.KNeighborsClassifier(n_neighbors=neighbor, algorithm='ball_tree')
    clf.fit(X, y)

    return clf


## Make Overlapping Time Window

def make_overlapping(X, y, window_length = 60):
    length = X.shape[0]
    X_new = []
    y_new = []

    for i in range(length):
        X_temp = []
        for j in range(window_length):
            if(i+j<length):
                X_temp.append(X[i+j])

        if(i+window_length-1<length):
            X_new.append(X_temp)
            y_new.append(y[i+window_length-1])

    return np.array(X_new), np.array(y_new)


## Concatenate X,Y,Z Axis into 1-D Numpy Array

def concat_xyz(X):
    X_concat = []
    for X_i in X:
        X_tp = X_i.transpose()
        X_stack = np.hstack((X_tp[0],X_tp[1],X_tp[2]))
        X_concat.append(X_stack)

    return np.array(X_concat)

## Reshape Data (Impure Label)

def prepare_impure_label(X, y, window_length=60):
    if(X.shape[0]<window_length):
        return [], []

    X_ol, y_ol = make_overlapping(X, y)
    X_concat_ol = concat_xyz(X_ol)

    return X_concat_ol, y_ol


label_list = ['sit', 'sleep', 'stand', 'walk']
label_dict = {'sit': 0, 'sleep': 1, 'stand': 2, 'walk': 3}
LABELS = label_list