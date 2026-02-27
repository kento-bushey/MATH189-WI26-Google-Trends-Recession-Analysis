import os

# Path to the directory you want to count
directory = "../../Data/Raw/Keywords/Frugality"

# Count only files (skip subdirectories)
file_count = sum(1 for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))

print(f"Number of files in '{directory}': {file_count}")