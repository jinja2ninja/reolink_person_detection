import os
import shutil
def reset_directories(directory, camera):
  if not os.path.exists(directory):
    os.mkdir(directory)
  if not os.path.exists(f"{directory}{camera}"):
    os.mkdir(f"{directory}{camera}")
  if not os.path.exists(f"{directory}{camera}/.tmp"):
    os.mkdir(f"{directory}{camera}/.tmp")
  elif os.path.exists(f"{directory}{camera}/.tmp"):
    # remove tmp directory and its contents, then recreate it
    shutil.rmtree(f"{directory}{camera}/.tmp")
    os.mkdir(f"{directory}{camera}/.tmp")