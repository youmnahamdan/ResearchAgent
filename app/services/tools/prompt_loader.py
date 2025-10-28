import os 

def prompt_loader(prompt_file):
    file_dir = f"services/prompts/{prompt_file}"
    if os.path.exists(file_dir):
        with open(file_dir, "r") as file:
            return file.read()
    
