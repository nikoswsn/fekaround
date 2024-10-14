from settings import OUTPUT_DIR


def mkdir_if_none(dir_path):
    '''Create directory if it doesn't exist'''
    from os import path, makedirs
    if not path.exists(dir_path):
        makedirs(dir_path)
        

def dir_ls(dir_path):
    '''Return a list of all filenames in the directory given'''
    import os
    try:
        file_names = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        return file_names
    except FileNotFoundError:
        print(f"Error: Directory '{dir_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def load_json_data(filepath):
    '''Open and return parsed .json file'''
    from json import load, JSONDecodeError
    try:
        with open(filepath, 'r', encoding='utf-8') as json_file:
            data = load(json_file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except JSONDecodeError:
        print(f"Error: File '{filepath}' is not a valid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def save_as_json(obj, path):
    import json
    with open(path, 'w', encoding="utf-8") as json_file:
        json.dump(obj, json_file, ensure_ascii=False, indent=2)
        
def read_txt(relative_path):
    '''Returns content of a .txt file'''
    with open(OUTPUT_DIR / relative_path, 'r') as f:
        content = f.read()
    return content

def read_txt_lines(relative_path):
    '''Returns lines of a .txt file'''
    with open(OUTPUT_DIR / relative_path, 'r') as f:
        lines = f.readlines()
    return lines

def save_txt(txt, relative_path):
    with open(OUTPUT_DIR / relative_path, "w") as file:
        file.write(txt)