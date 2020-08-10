import importlib
import os.path


def resolve(name, default=None):
    if name:
        if callable(name):
            return name
        (modname, dot, fnc) = str(name).rpartition(".")
        mod = importlib.import_module(modname)
        return getattr(mod, fnc) if hasattr(mod, fnc) and callable(getattr(mod, fnc)) else default
    else:
        return resolve(default, None) if not callable(default) else default


def mimetype_for_file(f):
    _, ext = os.path.splitext(f)
    return mimetype_for_extension(ext)


def mimetype_for_extension(extension):
    return mimetypesByExtension.get(extension, "application/octet-stream")


def extensions_for_mimetype(mimetype):
    return extensionByMimeType.get(mimetype, ".bin")


def primary_extension_for_mimetype(mimetype):
    extensions = extensions_for_mimetype(mimetype)
    return extensions[0] if len(extension) > 0 else None


mimetypesByExtension = {}
extensionByMimeType = {}

mimetypesByExtension[".aac"] = "audio/aac"
mimetypesByExtension[".abw"] = "application/x-abiword"
mimetypesByExtension[".arc"] = "application/x-freearc"
mimetypesByExtension[".avi"] = "video/x-msvideo"
mimetypesByExtension[".azw"] = "application/vnd.amazon.ebook"
mimetypesByExtension[".bin"] = "application/octet-stream"
mimetypesByExtension[".bmp"] = "image/bmp"
mimetypesByExtension[".bz"] = "application/x-bzip"
mimetypesByExtension[".bz2"] = "application/x-bzip2"
mimetypesByExtension[".csh"] = "application/x-csh"
mimetypesByExtension[".css"] = "text/css"
mimetypesByExtension[".csv"] = "text/csv"
mimetypesByExtension[".doc"] = "application/msword"
mimetypesByExtension[".docx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
mimetypesByExtension[".eot"] = "application/vnd.ms-fontobject"
mimetypesByExtension[".epub"] = "application/epub+zip"
mimetypesByExtension[".gz"] = "application/gzip"
mimetypesByExtension[".gif"] = "image/gif"
mimetypesByExtension[".htm"] = "text/html"
mimetypesByExtension[".html"] = "text/html"
mimetypesByExtension[".ico"] = "image/vnd.microsoft.icon"
mimetypesByExtension[".ics"] = "text/calendar"
mimetypesByExtension[".jar"] = "application/java-archive"
mimetypesByExtension[".jpeg"] = "image/jpeg"
mimetypesByExtension[".jpg"] = "image/jpeg"
mimetypesByExtension[".js"] = "text/javascript"
mimetypesByExtension[".json"] = "application/json"
mimetypesByExtension[".jsonld"] = "application/ld+json"
mimetypesByExtension[".mid"] = "audio/x-midi"
mimetypesByExtension[".midi"] = "audio/x-midi"
mimetypesByExtension[".mjs"] = "text/javascript"
mimetypesByExtension[".mp3"] = "audio/mpeg"
mimetypesByExtension[".mpeg"] = "video/mpeg"
mimetypesByExtension[".mpkg"] = "application/vnd.apple.installer+xml"
mimetypesByExtension[".odp"] = "application/vnd.oasis.opendocument.presentation"
mimetypesByExtension[".ods"] = "application/vnd.oasis.opendocument.spreadsheet"
mimetypesByExtension[".odt"] = "application/vnd.oasis.opendocument.text"
mimetypesByExtension[".oga"] = "audio/ogg"
mimetypesByExtension[".ogv"] = "video/ogg"
mimetypesByExtension[".ogx"] = "application/ogg"
mimetypesByExtension[".opus"] = "audio/opus"
mimetypesByExtension[".otf"] = "font/otf"
mimetypesByExtension[".png"] = "image/png"
mimetypesByExtension[".pdf"] = "application/pdf"
mimetypesByExtension[".php"] = "application/php"
mimetypesByExtension[".ppt"] = "application/vnd.ms-powerpoint"
mimetypesByExtension[".pptx"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
mimetypesByExtension[".rar"] = "application/vnd.rar"
mimetypesByExtension[".rtf"] = "application/rtf"
mimetypesByExtension[".sh"] = "application/x-sh"
mimetypesByExtension[".svg"] = "image/svg+xml"
mimetypesByExtension[".swf"] = "application/x-shockwave-flash"
mimetypesByExtension[".tar"] = "application/x-tar"
mimetypesByExtension[".tif"] = "image/tiff"
mimetypesByExtension[".tiff"] = "image/tiff"
mimetypesByExtension[".ts"] = "video/mp2t"
mimetypesByExtension[".ttf"] = "font/ttf"
mimetypesByExtension[".txt"] = "text/plain"
mimetypesByExtension[".vsd"] = "application/vnd.visio"
mimetypesByExtension[".wav"] = "audio/wav"
mimetypesByExtension[".weba"] = "audio/webm"
mimetypesByExtension[".webm"] = "video/webm"
mimetypesByExtension[".webp"] = "image/webp"
mimetypesByExtension[".woff"] = "font/woff"
mimetypesByExtension[".woff2"] = "font/woff2"
mimetypesByExtension[".xhtml"] = "application/xhtml+xml"
mimetypesByExtension[".xls"] = "application/vnd.ms-excel"
mimetypesByExtension[".xlsx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
mimetypesByExtension[".xml"] = "text/xml"
mimetypesByExtension[".xul"] = "application/vnd.mozilla.xul+xml"
mimetypesByExtension[".zip"] = "application/zip"
mimetypesByExtension[".3gp"] = "audio/3gpp"
mimetypesByExtension[".3g2"] = "audio/3gpp2"
mimetypesByExtension[".7z"] = "application/x-7z-compressed"

for extension, mimetype in mimetypesByExtension.items():
    current = extensionByMimeType.get(mimetype)
    if current is not None:
        extensionByMimeType[mimetype] = current.append(extension)
    else:
        extensionByMimeType[mimetype] = [extension]

