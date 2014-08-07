#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from bottle import *
import libs.chmod as chmod
import sys, os, time, md5, urllib2, json

app = Bottle()
full_path = os.path.abspath(os.path.dirname(sys.argv[0]))
app_dir = '/filemanager'
accounts = {"test": "test", "test2": "test2"} 
admins = ["test2"]
exclude = []

# Some code from https://github.com/herrerae/mia
def get_file_type(filename):
    path = request.GET.get('path')
    if not path:
        path = '/'
    TEXT_TYPE = ['doc', 'docx', 'txt', 'rtf', 'odf', 'text', 'nfo']
    AUDIO_TYPE = ['aac', 'mp3', 'wav', 'wma', 'm4p', 'flac']
    IMAGE_TYPE = ['bmp', 'gif', 'jpg', 'jpeg', 'png','svg']
    IMAGESOURCE_TYPE = ['eps', 'ico', 'psd', 'psp', 'raw', 'tga', 'tif', 'tiff', 'svg']
    VIDEO_TYPE = ['mv4', 'bup', 'mkv', 'ifo', 'flv', 'vob', '3g2', 'bik', 'xvid', 'divx', 'wmv', 'avi', '3gp', 'mp4', 'mov', '3gpp', '3gp2', 'swf', 'mpg', 'mpeg']
    COMPRESS_TYPE = ['7z', 'dmg', 'rar', 'sit', 'zip', 'bzip', 'gz', 'tar', 'ace']
    EXEC_TYPE = ['exe', 'msi', 'mse']
    SCRIPT_TYPE = ['js', 'html', 'htm', 'xhtml', 'jsp', 'asp', 'aspx', 'php', 'xml', 'css', 'py', 'bat', 'sh', 'rb', 'java']

    if os.path.isdir(full_path + path + "/" + filename):
        return "folder"
    else:
        extension = os.path.splitext(filename)[1].replace('.','')
        if extension in TEXT_TYPE:
            type_file = 'text'
        elif extension in AUDIO_TYPE:
            type_file = 'audio'
        elif extension in IMAGE_TYPE:
            type_file = 'imagen'
        elif extension in IMAGESOURCE_TYPE:
            type_file = 'imagesource'
        elif extension in VIDEO_TYPE:
            type_file = 'video'
        elif extension in COMPRESS_TYPE:
            type_file = 'compress'
        elif extension in EXEC_TYPE:
            type_file = 'exec'
        elif extension in SCRIPT_TYPE:
            type_file = 'script'
        elif extension == 'pdf':
            type_file = 'pdf'
        else:
            type_file = 'unknow'
        return type_file

# Some code from https://github.com/herrerae/mia
def date_file(path):
    mtime = time.gmtime(os.path.getmtime(path))
    return time.strftime("%d/%m/%Y %H:%M:%S", mtime)

# Some code from https://github.com/herrerae/mia
def convert_bytes(path):
    bytes = float(os.path.getsize(path))
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2f Tb' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2f Gb' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2f Mb' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2f Kb' % kilobytes
    else:
        size = '%.2f Bytes' % bytes
    return size

@app.post(app_dir+'/login')
def login():
    login = request.forms.get('login')
    password = request.forms.get('password')
    if not login or not password:
        redirect(app_dir+"/?error=empty")
    if login in accounts:
        if accounts[login] == password:
            hash = md5.new()
            hash.update(password)
            response.set_cookie("login", login)
            response.set_cookie("password", hash.hexdigest())
            redirect(app_dir+"/")
        else:
            redirect(app_dir+"/?error=badpass")
    else:
	# don't indicate if that's a valid user
        redirect(app_dir+"/?error=badpass")
    return ""

@app.route(app_dir+'/logout')
def logout():
    response.set_cookie("login", "")
    response.set_cookie("password", "")
    redirect(app_dir+"/")

@app.route(app_dir+'/img/:filename')
def img_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/')

@app.route(app_dir+'/img/view')
def view_img_static():
    filename = request.GET.get('path')
    return static_file(filename, root=full_path)

@app.route(app_dir+'/thumb')
def view_img_static():
    filename = request.GET.get('path')
    return static_file(filename, root=full_path)

@app.route(app_dir+'/img/icons/:filename')
def icons_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/icons/')

@app.route(app_dir+'/img/fancybox/:filename')
def fancybox_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/fancybox/')

@app.route(app_dir+'/js/:filename')
def js_static(filename):
    return static_file(filename, root=full_path+'/views/static/js/')

@app.route(app_dir+'/css/:filename')
def css_static(filename):
    return static_file(filename, root=full_path+'/views/static/css/')

@app.route(app_dir+'/upload', method='POST')
def do_upload():
    name = request.forms.get('name')
    print name
    path = request.forms.get('path').replace("/" + name, "")
    data = request.files.get('file')
    if not os.path.isdir(full_path + path + "/.thumbs"):
        os.mkdir(full_path + path + "/.thumbs")
    try:
        os.remove(full_path + path + "/.thumbs/" + name + ".jpg")
    except:
        print "File doesn't exists"
    thumb = open(full_path + path + "/.thumbs/" + name + ".jpg", "w+")
    thumb.write(data.file.read())
    return redirect(app_dir+"/?path=" + path)

@app.route(app_dir+'/delete')
def delete():
    try:
        os.remove(full_path + request.GET.get('path'))
        print full_path + request.GET.get('path')
    except:
        print "File doesn't exists"
    return redirect(app_dir+"/?path=" + str(request.GET.get('return')))

@app.route(app_dir+'/description', method='POST')
def description():
    f = full_path + request.forms.get('dir') + "/.settings"
    new_settings = json.loads('{"' + request.forms.get('name') + '": "' + request.forms.get('description') + '"}')
    if os.path.exists(f):
        settings_file = open(f, "r+")
        settings_json = json.load(settings_file)
        settings_json[request.forms.get('name')] = request.forms.get('description')
        settings_file.close()
        settings_file = open(f, "w")
        settings_file.write(json.dumps(settings_json))
        settings_file.close()
    else:
        settings_file = open(f, "w")
        settings_file.write(json.dumps(new_settings))
    settings_file.close()
    return redirect(app_dir+"/?path=" + request.forms.get('dir'))

@app.route(app_dir+'/download')
def download():
    filename = request.GET.get('path')
    return static_file(filename, root=full_path, download=filename)

@app.route('/')
def redirect_home():
    return redirect(app_dir+'/')

@app.route(app_dir+'/')
@view('main')
def list():
    if request.get_cookie("login") in admins:
        is_admin = True
    else:
        is_admin = False
    for header in response.headers:
        print header
    path = request.GET.get('path')
    if not path:
        path = '/'
    if path != '/':
        array = path.split("/")
        toplevel = path.replace("/" + array[path.count("/")], "")
        if not toplevel:
            toplevel  = '/'
    else:
        toplevel = False
    dirList = os.listdir(full_path + path)
    f = full_path + path + "/.settings"
    if os.path.exists(f):
        settings_file = open(f, "r+")
        settings_json = json.load(settings_file)
        settings_file.close()
    dirList.sort()
    output = []
    i = 1
    for item in dirList:
        if item in exclude:
            pass
        else:
            if not toplevel:
                filepath = path + item
            else:
                filepath = path + "/" + item
            if os.path.exists(full_path + path + "/.thumbs/" + item + ".jpg"):
                preview = path + "/.thumbs/" + item + ".jpg"
            else:
                preview = False
            if os.path.exists(f) and settings_json.get(item):
                description = settings_json[item]
            else:
                description = ''
            file = full_path + path + '/' + item
            output.append({"name": item, "path": filepath, "type": get_file_type(item),
                "date": date_file(full_path +filepath), "size": convert_bytes(full_path + filepath),
                "preview": preview, "counter": i, "description": description,
                "chmod":chmod.get_pretty_chmod(file)})
            i = i + 1
    data = {"title": path, "full_path": full_path, "path": path, "list": dirList,
        "toplevel": toplevel, "output": output, "login": request.get_cookie("login"),
        "password": request.get_cookie("password"), "error": request.GET.get('error'),
        "is_admin": is_admin, "app_dir": app_dir}
    return dict(data=data)

debug(True)
run(app, host='127.0.0.1', port=8082, reloader=True)
