# FIT VUT Regex Analyzer

## For Windows:

### Install Chocolatey (if not already installed):

Using PowerShell:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Using Command Prompt:
```
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
```
### Install Universal Ctags:
```
choco install universal-ctags
```

## For Linux:

### Install Universal Ctags:
```
sudo apt install universal-ctags
```
## Usage
```
usage: main.py [-h] [--nocolor] c_file
```
### Example
Run the C file analyzer:
```
main.py c_file.c
```
Run the C file analyzer without color:

```
main.py c_file.c --nocolor
```

