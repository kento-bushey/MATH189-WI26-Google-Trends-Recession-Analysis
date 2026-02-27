import os

directory = "../../Data/Raw/Keywords/Credit_and_debt"

for filename in os.listdir(directory):
    old_path = os.path.join(directory, filename)
    if os.path.isfile(old_path) and "_2004_2025" in filename:
        new_filename = filename.replace("_2004_2025", "")
        new_path = os.path.join(directory, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_filename}")

print("Done renaming files.")