import pandas as pd
import subprocess


# Load the Excel file
excel_file = 'viral_scripts.xlsx'
df = pd.read_excel(excel_file)

# Ensure the DataFrame has a column Script
if 'Script' not in df.columns:
    print("Column Script not found in the Excel file.")
else:
    # Iterate over each row and write the content of column B to a text file
    for index, row in df.iterrows():
        content = row['Script']
        file_name = f'prompt_{index + 1:02d}.txt'
        with open(file_name, 'w') as file:
            file.write(content)
        print(f"Saved {file_name}")
        command = f"python3.11 app.py --script {file_name} --method video"
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.decode().strip())

        
        rc = process.poll()
        #return rc # Removed return statement from the loop.

print("Process completed.")
print("Process completed.")