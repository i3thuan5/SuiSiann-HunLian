FROM i3thuan5/hok8-bu7
MAINTAINER i3thuan5

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install https://github.com/Taiwanese-Corpus/hue7jip8/archive/master.zip

RUN python manage.py migrate
RUN python manage.py 教典音檔0下載 dropbox
RUN find 語料 -name 54795.mp3 -delete
RUN python manage.py 教典音檔1轉檔
RUN python manage.py 教典音檔2匯入
RUN python manage.py 新北市900例句
RUN python manage.py SuiSiann

