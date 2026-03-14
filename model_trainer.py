import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# 1. Load Dataset
df = pd.read_csv('edu2job_1000.csv')

# 2. Data Cleaning & Feature Selection (As per slides)
df = df.drop(['S.No', 'Student_ID'], axis=1)

# 3. Encoding Categorical Variables
# Mapping Yes/No to 1/0
binary_cols = ['Python', 'Java', 'SQL', 'Machine_Learning', 'Web_Development', 'Internship_Experience']
for col in binary_cols:
    df[col] = df[col].map({'Yes': 1, 'No': 0})

# Mapping Communication Skills
df['Communication_Skills'] = df['Communication_Skills'].map({'Low': 0, 'Medium': 1, 'High': 2})

# Label Encoding for the Target variable
le = LabelEncoder()
df['Predicted_Job_Role'] = le.fit_transform(df['Predicted_Job_Role'])

# 4. Train-Test Split (80-20 as per slides)
X = df.drop('Predicted_Job_Role', axis=1)
y = df['Predicted_Job_Role']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# 5. Model Training (Selected Model: Random Forest)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 6. Save Model and Label Encoder
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Model trained and saved successfully!")