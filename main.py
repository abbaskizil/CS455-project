from git import Repo
import os
import glob
import shutil
import stat
import pathlib

def redo_with_write(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)

# GLOBAL VARIABLES
current_directory = pathlib.Path().resolve()
repo_exists = os.path.isdir("temp/")
source_code_extensions = (
    ".py", ".ipynb",".cpp",".js", ".ts", ".java", ".go", 
    ".rs", ".c", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
    ".scala", ".r", ".m", ".sh"
    )

# if not repo_exists:
#     git_url = "https://github.com/omuremreyildiz03/song2vec"
#     repo_dir = "temp/"

#     Repo.clone_from(git_url, repo_dir)

# else:
#     shutil.rmtree("temp/", onerror = redo_with_write)

file_list = [(curDir,f) for curDir, subDir, files in os.walk("temp/") for f in files if f.endswith(source_code_extensions)]
for f in file_list:
    norm_path = os.path.normpath(os.path.join(current_directory, f[0], f[1]))
    print(norm_path)
