from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load the saved model and label encoder
model = pickle.load(open('model.pkl', 'rb'))
le = pickle.load(open('label_encoder.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Getting data from form
    features = [
        float(request.form['cgpa']),
        1 if request.form['python'] == 'Yes' else 0,
        1 if request.form['java'] == 'Yes' else 0,
        1 if request.form['sql'] == 'Yes' else 0,
        1 if request.form['ml'] == 'Yes' else 0,
        1 if request.form['webdev'] == 'Yes' else 0,
        int(request.form['comm']),
        1 if request.form['internship'] == 'Yes' else 0,
        int(request.form['projects']),
        int(request.form['certs'])
    ]
    
    final_features = [np.array(features)]
    prediction = model.predict(final_features)
    output = le.inverse_transform(prediction)[0]

    return render_template('result.html', prediction_text=f'Recommended Job Role: {output}')

if __name__ == "__main__":
    app.run(debug=True)