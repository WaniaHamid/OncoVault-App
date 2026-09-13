import sys
print("Python version:", sys.version)
print("Importing numpy...")
import numpy as np
print("Imported numpy:", np.__version__)
print("Importing sklearn...")
import sklearn
print("Imported sklearn:", sklearn.__version__)
print("Importing LogisticRegression...")
from sklearn.linear_model import LogisticRegression
print("Importing RandomForest...")
from sklearn.ensemble import RandomForestClassifier
print("All imports successful!")
