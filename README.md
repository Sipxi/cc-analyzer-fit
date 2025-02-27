# FIT VUT Regex Analyzer

## About
I was bored and pissed off that automatic tests will grade our syntax and so on, so I decided to replicate their (university's) syntax checker using **regex** and **Python**. (Don't ask me why regex, it just felt right.)

## Features
- 🔍 **Syntax checking**: Checks if your code doesn't have anything bad(FIT VUT opinion)
- 🎨 **Color and no color mode**: Run with fancy colors or not(My classmate had problems with colors in terminal, so i decided to make no color flag)

## Setup

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

