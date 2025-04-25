# CPT Platform
A simple platform for competitive programming tournaments

https://phscpt.pythonanywhere.com

## Capabilities
- [x] Hosting contests, with live-updating scoreboards
- [x] Intuitive problem-setting interface
- [x] Grader support for Python, Java and C++
- [x] Persistent Scoreboards across system restarts
- [x] Client-side storage of problem results
- [ ] User accounts

## KNOWN BUGS
- Past problem results may appear on the client side for 2 players on 1 browser account (or otherwise with shared localstorage)
- Sorting appears to persist, but actually doesn't...

## Dependencies
Requires python `markdown` and `flask` libraries, as well as `g++`, `java`, `python2.7` and `python3.9`.

## Usage
- Use a WSGI of your choosing to host the website in main.py
- Run `grader.py` on the _same machine_
  - You _can_ run multiple graders, but they have a decently high chance of racing for any given submission so it's highly discouraged