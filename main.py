#!/usr/local/bin/python3
import zipfile
from lxml import etree
from flask import Flask, render_template, send_file, request, make_response
import os
import re

XML_NAMESPACE = {
    "n": "urn:oasis:names:tc:opendocument:xmlns:container",
    "pkg": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
}
BASE = "/data"


def get_epub_info(fname):
    ret = {}
    tree, path = open_epub(fname)

    if tree is None:
        return None

    p = tree.xpath("/pkg:package/pkg:metadata", namespaces=XML_NAMESPACE)[0]
    for s in ["title", "language", "creator", "date"]:
        ret[s] = p.xpath("dc:%s/text()" % (s), namespaces=XML_NAMESPACE)[0]

    ret["date"] = ret["date"][:9]

    return ret


def open_epub(fname):
    zip = zipfile.ZipFile(fname)
    try:
        try:
            path = "OEBPS/"
            tree = etree.fromstring(zip.read(path + "content.opf"))
        except:
            path = ""
            tree = etree.fromstring(zip.read(path + "content.opf"))
        return (tree, path)
    except:
        return (None, None)


def get_image(bookPath):
    zip = zipfile.ZipFile(bookPath)
    tree, path = open_epub(bookPath)
    if tree is None:
        return None
    m = tree.xpath("/pkg:package/pkg:manifest/pkg:item", namespaces=XML_NAMESPACE)
    for i in m:
        if i.xpath("@media-type")[0][0:5] == "image" and (
            (len(i.xpath("@id")) > 0 and i.xpath("@id")[0].lower().find("cover") > -1)
            or i.xpath("@href")[0].lower().find("cover") > -1
            or (
                len(i.xpath("@properties")) > 0
                and i.xpath("@properties")[0] == "cover-image"
            )
        ):
            return zip.read(path + i.xpath("@href")[0])


def find_first_book(path):
    for i in os.listdir(path):
        if os.path.isdir(i):
            r = find_first_book(os.path.join(path, i))
            if r is not None:
                return r
        elif i[-4:] == "epub":
            return os.path.join(path, i)
    return None


def list_books(full_path, num_path):
    books = []
    x = 0
    if len(num_path) > 0:
        if num_path[0] == "/":
            num_path = num_path[1:]
        if num_path[-1] != "/":
            num_path += "/"

    for i in sorted(os.listdir(full_path)):
        p = os.path.join(full_path, i)
        if os.path.isdir(p):
            books.append(
                {
                    "title": i,
                    "language": "",
                    "creator": "Directory",
                    "date": "",
                    "link": num_path + str(x),
                }
            )
        elif i[-4:] == "epub":
            data = get_epub_info(p)
            if data is None:
                data = {
                    "title": i,
                    "language": "/",
                    "creator": "Unknown",
                    "date": "",
                    "link": num_path + str(x),
                }
            else:
                data["link"] = num_path + str(x)
                books.append(data)
        x += 1
    return books


def num_to_path(base, p):
    path = base
    if p not in ["", "/", "favicon.ico"]:
        for i in p.split("/"):
            path = os.path.join(path, sorted(os.listdir(path))[int(i)])
    return path


app = Flask(__name__)


@app.route("/")
@app.route("/<path:path>")
def index(path=""):
    lang = re.findall("[a-z]{2}_[A-Z]{2}", path)
    if len(lang) > 0:
        lang = lang[0]
        path = path[5:]
        if len(path) > 0 and path[0] == "/":
            path = path[1:]

    page = int(request.args["page"]) if "page" in request.args else 0

    if len(path) > 5 and path[-5:] == ".epub":
        path = path[0:-5]

    p = num_to_path(BASE, path)

    if p[-4:] == "epub":
        return send_file(
            p,
            as_attachment=True,
            download_name=os.path.basename(os.path.normpath(p)),
            mimetype="application/epub+zip",
        )
    else:
        lst = list_books(p, path)
        return render_template(
            "index.html", books=lst[page * 9 :], page=page, max_page=len(lst) // 9
        )


@app.route("/image/<path:path>")
def image(path):
    p = num_to_path(BASE, path)
    d = os.path.isdir(p)
    if d:
        p = find_first_book(p)

    try:
        img = get_image(p)
    except:
        return send_file("static/none.png")

    if img is None:
        return send_file("static/none.png")

    response = make_response(img)
    response.headers.set("Content-Type", "image/jpeg")
    return response


app.run(host="0.0.0.0", port=8080)