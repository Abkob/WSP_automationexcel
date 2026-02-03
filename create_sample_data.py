import pandas as pd
import numpy as np

np.random.seed(42)

data = {
    'Student_ID': range(1, 201),
    'Name': [f'Student_{i}' for i in range(1, 201)],
    'GPA': np.random.uniform(2.0, 4.0, 200).round(2),
    'Status': np.random.choice(['Active', 'Probation', 'Suspended', 'Graduate'], 200),
    'Department': np.random.choice(['CSE', 'Math', 'Physics', 'Biology', 'Chemistry'], 200),
    'Scholarship': np.random.choice([0, 500, 1000, 1500, 2000, 2500], 200),
    'Year': np.random.choice([1, 2, 3, 4, 5], 200),
    'Credits': np.random.randint(0, 180, 200),
}

df = pd.DataFrame(data)
df.to_excel('sample_students.xlsx', index=False)
print("Created sample_students.xlsx with 200 rows")
