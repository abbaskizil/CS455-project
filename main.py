# Standard library
import os
import glob
import shutil
import stat
import pathlib

# Third party
from git import Repo

# Local
import chunker

# GLOBAL VARIABLES
current_directory = pathlib.Path().resolve()
repo_exists = os.path.isdir("temp/")
source_code_extensions = (".py", ".ipynb",".cpp", ".c", ".h", ".hpp", ".js", ".ts", ".java", ".go")

def redo_with_write(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)

# if not repo_exists:
#     git_url = "https://github.com/omuremreyildiz03/spotify-wrap-demo"
#     repo_dir = "temp/"

#     Repo.clone_from(git_url, repo_dir)

# else:
#     shutil.rmtree("temp/", onerror = redo_with_write)

file_list = []
path_list = [(curDir,fl) for curDir, subDir, files in os.walk("temp/") for fl in files if fl.endswith(source_code_extensions)]
for f in path_list:
    norm_path = os.path.normpath(os.path.join(current_directory, f[0], f[1]))
    file_list.append(norm_path)

for file in file_list:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        extension = "." + file.split(".")[-1]
        chunker.Python_Parser(file, content, extension)
