
   **!!! UNDER CONSTRUCTION !!!**


# flask-file-server

A flask file server with an elegant frontend for 
  - browsing, 
  - uploading and streaming
  - copying, moving, deleting
#  - annotating
  - sending
files

Files are stored in a non-redundant way by symlinks.

Additional custom actions can be implemented for several events.

![screenshot](https://raw.githubusercontent.com/zellerede/flask-file-server/master/screenshot.jpg)

## Run
```docker run -v /target/folder/on/host:/data -p 8000:8000 zellerede/flask-file-server```

## Params
FS_BIND = Param for bind address, default 0.0.0.0  
FS_PORT = Param for server port, default 8000  
FS_PATH = Param for serve path, default /data
FS_KEY = Param for authentication key as base64 encoded username:password, default none  

```docker run -v /data:/data -v /path/to/custom_actions:/src -p 8000:8000 -e FS_BIND=0.0.0.0 -e FS_PORT=8000  -e FS_PATH=/tmp -e FS_KEY=dGVzdDp0ZXN0 zellerede/flask-file-server```

## Custom actions

For usage, see example/custom_actions.py.

# Contribute

## Prerequisites
```pip install -r requirements.txt```

## Build docker
```docker build -t zellerede/flask-file-server:latest .```

## TODO:
  - Add tests!!
  - Refactor existing code
  - Add pure json answers
  - Add custom actions for events like before/after file upload/download, copy/move/delete
  - Introduce Backend Database for file annotations, checksums and filesets
  - Introduce Fileset Replication (through e.g. /api/fileset/<id>/replicate?to=<ip> --> /api/fileset/receive,  later: predefined authenticated connections)
  - Enhance authentication: Role Based Access for base folders 'repositories' (as a prototype we might simply use different Unix users)
     -- see e.g. https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
