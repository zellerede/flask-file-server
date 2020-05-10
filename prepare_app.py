from flask import Flask
from datetime import datetime
import humanize
from pathlib2 import Path
import os

app = Flask(__name__, static_url_path='/assets', static_folder='assets')
root = Path(os.getenv('FS_PATH', '/tmp')).absolute()
store = root / '.store'
key = os.getenv('FS_KEY', '')

ignored = [
    '.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg', '.htaccess',
    '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX', 'ehthumbs.db',
    'Thumbs.db', 'thumbs.tps', '.store'
]
datatypes = {
    'audio': 'm4a,mp3,oga,ogg,webma,wav', 'archive': '7z,zip,rar,gz,tar',
    'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf',
    'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt',
    'source': 'atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml,plist',
    'text': 'txt', 'video': 'mp4,m4v,ogv,webm', 'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'
}
icontypes = {
    'fa-music': 'm4a,mp3,oga,ogg,webma,wav', 'fa-archive': '7z,zip,rar,gz,tar',
    'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'fa-file-text': 'pdf',
    'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt,mp4,m4v,ogv,webm',
    'fa-code': 'atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml',
    'fa-file-text-o': 'txt', 'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'
}


@app.template_filter('size_fmt')
def size_fmt(size):
    return humanize.naturalsize(size)


@app.template_filter('time_fmt')
def time_desc(timestamp):
    mdate = datetime.fromtimestamp(timestamp)
    str = mdate.strftime('%Y-%m-%d %H:%M:%S')
    return str


@app.template_filter('data_fmt')
def data_fmt(filename):
    t = 'unknown'
    for type, exts in datatypes.items():
        if filename.split('.')[-1] in exts:
            t = type
    return t


@app.template_filter('icon_fmt')
def icon_fmt(filename):
    i = 'fa-file-o'
    for icon, exts in icontypes.items():
        if filename.split('.')[-1] in exts:
            i = icon
    return i


@app.template_filter('humanize')
def time_humanize(timestamp):
    mdate = datetime.utcfromtimestamp(timestamp)
    return humanize.naturaltime(mdate)


def relative(path):
    return path[(len(str(root)) + 1):]


#
store.mkdir(parents=True, exist_ok=True)
