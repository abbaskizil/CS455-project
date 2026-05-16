from git import Repo
import os
import glob
import shutil
import stat

def redo_with_write(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)

repo_exists = os.path.isdir("temp/")

if not repo_exists:
    git_url = "https://github.com/omuremreyildiz03/song2vec"
    repo_dir = "temp/"

    Repo.clone_from(git_url, repo_dir)


else:
    shutil.rmtree("temp/", onerror = redo_with_write)

