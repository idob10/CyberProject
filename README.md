# Cyber 5 points project

## Prerequisites
This project requires Python (version 3.8 or later) and the following libraries:
- socket
- time
- os
- sys
- watchdog
- string
- random
- threading
- AES
- requests
- simplejson
- httplib2
- json
- win32con

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Installation

**BEFORE YOU INSTALL :** please read the [prerequisites](#prerequisites)

Start with cloning this repo on your local machine:

```sh
$ git clone https://github.com/idob10/CyberProject.git
$ cd src
```

To install and set up the library, run:

```sh
$ pip install [libraryName]
```
## Usage

### Serving the app

```sh
$ python server.py [portNum] # server is running
$ python client.py [serverIP] [serverPORT] [libraryName] [numOfSeconds] # new user is connected to a new group
$ python client.py [serverIP] [serverPORT] [libraryName] [numOfSeconds] [token] # new user is connected to an existing group
$ 
```

## Features


## Author

* **Ido Barkai** - [Ido Barkai](https://github.com/idob10)