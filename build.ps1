pyinstaller.exe --clean --icon=images/battery.ico -F -w main.py
Copy-Item -Path "images" -Destination "dist/images" -Recurse -Force
Copy-Item  "config.json" -Destination "dist/config.json" -Recurse -Force