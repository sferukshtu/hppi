from app import app
import os

""" watch the templates add reload app if something is changed there """
""" app/templates/count.html is updated in on_rating.view to reload app automatically if collection rating is changed """

extra_dirs = ['app/templates']
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)
app.run(extra_files=extra_files)
