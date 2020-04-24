
   **!!! UNDER CONSTRUCTION !!!**


# flask-file-server

A flask file server with an elegant frontend for 
  - browsing, 
  - uploading and streaming,
  - annotating
files

![screenshot](https://raw.githubusercontent.com/zellerede/flask-file-server/master/screenshot.jpg)

## Run
```docker run -p 8000:8000 zellerede/flask-file-server```

## Params
FS_BIND = Param for bind address, default 0.0.0.0  
FS_PORT = Param for server port, default 8000  
FS_PATH = Param for serve path, default /tmp  
FS_KEY = Param for authentication key as base64 encoded username:password, default none  

```docker run -p 8000:8000 -e FS_BIND=0.0.0.0 -e FS_PORT=8000  -e FS_PATH=/tmp -e FS_KEY=dGVzdDp0ZXN0 zellerede/flask-file-server```


# Contribute

## Prerequisites
```pip install -r requirements.txt```

## Build docker
```docker build --rm -t zellerede/flask-file-server:latest .```

## TODO:
  - Add tests!!
  - Refactor existing code
  - Introduce  Copy, Move, Delete operations (API first)
  - later in UI: right click menu
  - UI: Make folder
  - Introduce Backend Database for file annotations and checksums
  - Enhance authentication: Role Based Access for base folders 'repositories' (as a prototype, simply use different Unix users)
