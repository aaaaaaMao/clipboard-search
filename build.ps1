pyinstaller.exe --clean --icon=resources/images/battery.ico -F -w main.py
Copy-Item -Path "resources/images" -Destination "dist/resources/images" -Recurse -Force
Copy-Item -Path "configs" -Destination "dist/configs" -Recurse -Force