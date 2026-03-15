# Edu2Job: Skill Assessment & Mock Test Module

This module is a core part of the **Edu2Job** project, designed to provide students with an interactive platform to test and evaluate their technical knowledge in various Computer Science domains.

---

## ✨ Features

### 📝 Interactive Mock Tests
* **Multi-Subject Support:** Offers comprehensive tests for subjects like **Java Programming** and **Data Structures (DSA)**.
* **Timed Sessions:** Each assessment is equipped with a 30-minute countdown timer to simulate real-time exam scenarios.
* **Instant Evaluation:** Automated grading system that calculates scores immediately upon submission.
* **Detailed Review:** Users can review correct answers and their own choices after completing the test.

### 📊 Performance Tracking
* **Score Management:** Student performance data (Username, Subject, Score, Total) is persistently stored in a local **SQLite** database.
* **History Log:** Allows the platform to maintain a record of all attempted tests for future reference.

---

## 📂 Project Structure

Based on the current development environment, the project is organized as follows:

```text
EDU2JOB/
├── app.py                  # Main Flask application entry point
├── createdataset.py        # Dataset generation utility
├── model_trainer.py        # Script for training the ML model
├── database.db             # SQLite database for storing test scores
├── krishnanjali/           # Core Mock Test Module
│   ├── app.py              # Backend logic for the quiz system
│   └── template/           # UI components for the assessment
│       ├── mock_test.html  # Subject selection dashboard
│       └── test_page.html  # Interactive test interface
├── static/                 # Static assets (Images/Uploads)
└── templates/              # Base HTML templates

```
---
Component	Technology
Backend	Python, Flask
Database	SQLite3
Frontend	HTML5, CSS3 (Bootstrap 5), JavaScript
Templating	Jinja2

🚀 How to Run
Navigate to the Project Root:
Ensure you are in the EDU2JOB directory.

1.Install Required Libraries:
```text
Bash
pip install flask flask-cors
```
2.Start the Application:
```text
Bash
python app.py
```
3.Access the Module:
Open your web browser and visit: ``` http://localhost:5000/test/java ```

⚖️ License

This project is licensed under the MIT License.
