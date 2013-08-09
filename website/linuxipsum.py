#!/usr/bin/env python

import random

TEXT = "dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

WORDS = """\
source
software
cloud
project
Source
community
development
applications
projects
business
tools
services
presentation
innovation
information
application
management
solutions
OpenStack
platform
Cloud
developers
create
model
enterprise
technologies
users
logiciel
Linux
companies
features
communities
session
provide
market
large
public
collaboration
approach
people
Python
devops
open source
free software
Eclipse
Markdown
big data
open data
CSS
responsive
real time
HTML5
Android
""".split("\n")


def generate():
  output = []
  words = TEXT.split(" ")
  for word in words:
    if word.endswith("."):
      add_dot = True
      word = word[0:-1]
    else:
      add_dot = False
    if len(word) > 3 and random.random() > 0.3:
      word = random.choice(WORDS)
    if add_dot:
      word += "."
    output.append(word)
  return "Linux ipsum " + " ".join(output)


if __name__ == "__main__":
  print generate()
