from app import app
import os

""" watch the templates and reload app if something is changed there (due to updates or model changed: see the next line comment)"""
""" if app/templates/count.html is updated by on_rating.view then app is automatically reloaded (when collection rating is changed) """

watch_dirs = ['app/templates']
watch_files = watch_dirs[:]
for w_dir in watch_dirs:
    for dirname, dirs, files in os.walk(w_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                watch_files.append(filename)
app.run('0.0.0.0', extra_files=watch_files)
