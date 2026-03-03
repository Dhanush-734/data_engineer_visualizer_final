import pandas as pd
import random
import numpy as np

# Number of rows (change to 10000 if needed)
rows = 5000

departments = ["CSE", "IT", "ECE", "ME", "EEE", "Civil"]
skills_list = ["Python", "Java", "SQL", "ML", "React", "AutoCAD", "MATLAB"]
companies = ["Infosys", "TCS", "Wipro", "Amazon", "Google", "Microsoft", None]

data = []

for i in range(1, rows + 1):
    placed = random.choice(["Yes", "No"])
    
    if placed == "Yes":
        company = random.choice(companies[:-1])
        package = round(random.uniform(3.0, 20.0), 1)
    else:
        company = None
        package = 0.0

    data.append([
        1000 + i,
        f"Student_{i}",
        random.choice(departments),
        round(random.uniform(6.0, 9.8), 2),
        random.choice(skills_list),
        random.choice(["Yes", "No"]),
        placed,
        company,
        package
    ])

df = pd.DataFrame(data, columns=[
    "Student_ID",
    "Name",
    "Department",
    "CGPA",
    "Skills",
    "Internship",
    "Placed",
    "Company",
    "Package"
])

# Add some random missing values
for col in ["Company", "Skills"]:
    df.loc[df.sample(frac=0.1).index, col] = np.nan

df.to_csv("large_student_data.csv", index=False)

print("Large CSV file generated successfully!")