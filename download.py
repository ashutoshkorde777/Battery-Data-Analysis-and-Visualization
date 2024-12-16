import kagglehub
import os
import shutil


# Download latest version
path = kagglehub.dataset_download("patrickfleith/nasa-battery-dataset")

print("Path to dataset files:", path)


# Path to the dataset files
source_path = r"C:\Users\Lenovo\.cache\kagglehub\datasets\patrickfleith\nasa-battery-dataset\versions\2"

# Current working directory
current_directory = os.getcwd()

# Check if the source directory exists
if os.path.exists(source_path):
    # Loop through all files and folders in the source path
    for item in os.listdir(source_path):
        source_item = os.path.join(source_path, item)
        destination_item = os.path.join(current_directory, item)

        # Move file or directory
        if os.path.isdir(source_item):
            shutil.move(source_item, destination_item)
        else:
            shutil.move(source_item, current_directory)
    print(f"Files moved successfully to: {current_directory}")
else:
    print("Source path does not exist.")
