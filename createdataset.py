import pandas as pd
import random

# Configuration
num_rows = 1000
roles = ['Data Scientist', 'Full Stack Developer', 'ML Engineer', 'Backend Developer', 
         'Frontend Developer', 'Business Analyst', 'Data Analyst', 'Software Engineer']

data = []

for i in range(1, num_rows + 1):
    # Generating Features
    serial_no = i
    student_id = f"STU2026{i:04d}"
    cgpa = round(random.uniform(6.0, 10.0), 2)
    python = random.choice(['Yes', 'No'])
    java = random.choice(['Yes', 'No'])
    sql = random.choice(['Yes', 'No'])
    ml = random.choice(['Yes', 'No'])
    web_dev = random.choice(['Yes', 'No'])
    comm_skills = random.choice(['Low', 'Medium', 'High'])
    internship = random.choice(['Yes', 'No'])
    projects = random.randint(0, 5)
    certifications = random.randint(0, 6)
    
    # Simple logic for "Predicted Job Role" (The Target Variable)
    if ml == 'Yes' and python == 'Yes' and cgpa > 8.0:
        role = 'Data Scientist'
    elif ml == 'Yes' and python == 'Yes':
        role = 'ML Engineer'
    elif web_dev == 'Yes' and java == 'Yes':
        role = 'Full Stack Developer'
    elif web_dev == 'Yes':
        role = 'Frontend Developer'
    elif sql == 'Yes' and comm_skills == 'High':
        role = 'Business Analyst'
    elif python == 'Yes' or java == 'Yes':
        role = 'Software Engineer'
    else:
        role = 'Data Analyst'

    data.append([serial_no, student_id, cgpa, python, java, sql, ml, web_dev, comm_skills, internship, projects, certifications, role])

# Create DataFrame
columns = ['S.No', 'Student_ID', 'CGPA', 'Python', 'Java', 'SQL', 'Machine_Learning', 
           'Web_Development', 'Communication_Skills', 'Internship_Experience', 'Projects', 'Certifications', 'Predicted_Job_Role']

df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv('edu2job_1000.csv', index=False)
print("Dataset with 1000 rows generated successfully!")