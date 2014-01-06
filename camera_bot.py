#!/usr/bin/env python
#coding: utf-8

"Webカメラで撮った画像を返すLingrボット"

# Copyright (c) 2013 Yuki Fujii
# Licensed under the MIT License

from __future__ import division, print_function
import bottle
import logging
import os


app = bottle.Bottle()
root_path = os.path.dirname(__file__)
app.config.load_config(os.path.join(root_path, "camera_bot.conf"))


@app.get("/")
def index():
    return "Lingr Camera Bot"


@app.post("/")
def return_message():
    "Lingrからのリクエストに答える"

    req = bottle.request

    camera_num = int(app.config["camera.number"])
    save_dir = os.path.join(root_path, "picture")
    baseurl = app.config["app.url"]
    ret = ""
    for event in req.json["events"]:
        text = event["message"]["text"]
        room = event["message"]["room"]
        if text == app.config["lingr.command"] \
           and room == app.config["lingr.room"]:
            filename = take_picture(camera_num, save_dir)
            basename = os.path.basename(filename)
            ret = "{}{}".format(baseurl, basename)
            break

    return create_text_response(ret)


@app.get("/<filepath:path>")
def return_picture(filepath):
    "写真を静的ファイルとして返す"

    picture_dir = os.path.join(root_path, "picture")
    return bottle.static_file(filepath, root=picture_dir)


def take_picture(camera_num, dirname):
    "写真を撮って指定ディレクトリ以下に保存し，そのファイル名を返す"

    import cv2

    capture = cv2.VideoCapture(camera_num)
    if capture.isOpened() == False:
        logging.error("カメラが見つからない")
        bottle.abort(500, "cannot find a camera")

    ret, img = capture.read()
    filename = create_unique_filename(dirname)
    cv2.imwrite(filename, img)

    return filename


def create_unique_filename(dirname):
    "日時とランダム文字列を使って重複しないファイル名を作成する"

    import string
    import random
    import datetime

    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    source = string.digits + string.letters

    # NOTE: 名前衝突100回発生はありえないと考える
    for i in xrange(100):
        key = "".join([random.choice(source) for i in xrange(20)])
        name = now + "-" + key + ".jpg"
        filename = os.path.join(dirname, name)
        if not os.path.exists(filename):
            return filename

    logging.error("ユニークな名前を作れなかった")
    bottle.abort(500, "cannot create a unique filename")


def create_text_response(message, status=200):
    res = bottle.HTTPResponse(
        body=message,
        status=status
    )
    res.content_type = "text/plain; charset=UTF-8"
    return res


def parse_arguments():
    import optparse
    parser = optparse.OptionParser("usage: %prog [options]")
    parser.add_option("--host",
                      dest="host",
                      type="string",
                      default="localhost",
                      help="set the host",
                      metavar="HOST")
    parser.add_option("--port",
                      dest="port",
                      type="int",
                      default=8080,
                      help="set the port number",
                      metavar="PORT")
    parser.add_option("--mode",
                      dest="mode",
                      type="string",
                      default="development",
                      help="set the mode (development|production)",
                      metavar="MODE")
    (opts, args) = parser.parse_args()
    return opts


if __name__ == "__main__":
    opts = parse_arguments()
    log_format = "%(asctime)s %(message)s"
    log_file = os.path.join(root_path, "log", "{}.log".format(opts.mode))

    if opts.mode == "production":
        logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)
        logging.info("start lingr-camera-bot on production mode!")
        app.run(host=opts.host, port=opts.port, debug=False, reloader=False)
    else:
        logging.basicConfig(filename=log_file, format=log_format, level=logging.DEBUG)
        logging.info("start lingr-camera-bot on development mode!")
        app.run(host=opts.host, port=opts.port, debug=True, reloader=True)
