FROM i3thuan5/hapsing-giliau AS giliau
MAINTAINER i3thuan5
RUN pip install --upgrade https://github.com/i3thuan5/tai5-uan5_gian5-gi2_hok8-bu7/archive/Tacotron%E8%8E%AB%E6%8F%9B%E9%80%9D.zip
RUN python manage.py 匯出Tacotron格式資料 台語 王秀容 /opt/giliau



FROM tensorflow/tensorflow:latest-gpu-py3

#RUN pip install --upgrade pip

#RUN wget http://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2
# RUN tar -jxvf LJSpeech-1.1.tar.bz2
RUN apt-get update && apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools wget git vim

WORKDIR /opt
RUN git clone -b i3thuan5_working https://github.com/a8568730/Tacotron-2.git

WORKDIR Tacotron-2
RUN ln -s ../LJSpeech-1.1 .
RUN pip install -r requirements.txt

COPY --from=giliau /opt/giliau/taioanoe Taioanoe

COPY hparams.py taioanoe.py ./
RUN python taioanoe.py
RUN python train.py --model='Tacotron-2'


