import os


def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print(e)


def delete_all_files_in_directory(directory_path):
    try:
        # List all files in the directory
        files = os.listdir(directory_path)

        # Iterate through the files and delete them
        for file in files:
            file_path = os.path.join(directory_path, file)
            delete_file(file_path)

        print("All files in the directory have been deleted.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
