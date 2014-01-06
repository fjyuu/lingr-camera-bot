# Lingrカメラボット #

Webカメラで撮った画像を返すLingrボット

## 環境 ##

* Python 2.7.5
* OpenCV 2.4.6.1

## 実行 ##

まず，`camera_bot.conf.sample` を参考にして設定ファイル
`camera_bot.conf` を書く．

つぎに，以下のように起動する．

    $ python2.7 camera_bot.py --host localhost --port 8080

## 既知の問題 ##

* Lingrからのリクエストを偽装されると画像を返してしまう．

## ライセンス ##

MITライセンスです．
