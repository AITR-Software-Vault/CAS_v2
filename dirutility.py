import os
import uuid
import shutil
import pathlib
import config

def clean_up(dir):
    try:
        for file in os.listdir(dir):
            fpath = os.path.join(dir, file)
            os.remove(fpath)
            print("Cleanup:", file, "removed")
    except FileNotFoundError:
        print("No such directory exists: %s" % dir)


def create_dir(folder_path) -> str:
    parentPath = '.'
    # path = os.path.join(parentPath, folder_path)
    path = folder_path
    try:
        os.mkdir(path)
    except FileExistsError:
        clean_up(path)
    except FileNotFoundError:
        print(FileNotFoundError)
    finally:
        return path


def create_safe_dir(folder_path) -> str:
    parentPath = '.'
    path = folder_path
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    except FileNotFoundError:
        print(FileNotFoundError)
    finally:
        return path

def create_report_folder(filename) -> str:
    fname = filename.split('.')[0].strip()
    # homedir   = pathlib.Path(os.environ["USERPROFILE"])
    # targetdir = pathlib.Path(f'./data/reports/{fname}/')
    targetdir = pathlib.Path(config.REPORTSFOL) / fname
    try:
        os.makedirs(targetdir)
    except:
        clean_up(targetdir)
    return targetdir


def create_raw_folder() -> None:
    # targetdir = f'./data/raw/'
    targetdir = pathlib.Path(config.RAWFOL)
    os.makedirs(targetdir, exist_ok=True)


import re
def upload_to_raw_folder(filepath: str, survey_name: str = "", upload_time = None) -> str:
    targetdir = pathlib.Path(config.RAWFOL)
    sourcefile = pathlib.Path(filepath)
    extension = sourcefile.suffix
    
    if survey_name and survey_name.strip():
        base_name = survey_name.strip()
    else:
        base_name = sourcefile.stem
        
    # Clean up base_name for valid Windows folder/file naming
    base_name = re.sub(r'[\/*?:"<>|]', "", base_name).strip()
    
    if upload_time:
        if hasattr(upload_time, "isoformat"):
            time_str = upload_time.isoformat(timespec='seconds')
        else:
            time_str = str(upload_time)
        # Clean ISO time for valid filename (replace colons)
        time_str = time_str.replace(":", "-").replace(" ", "T")
        crypticname = f"{base_name}_{time_str}{extension}"
    else:
        crypticname = str(uuid.uuid1()) + extension
        
    destfile = targetdir / crypticname
    shutil.copy2(sourcefile, destfile)
    print("Copied", crypticname, destfile, extension)
    return crypticname