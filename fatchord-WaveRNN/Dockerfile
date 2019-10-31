FROM i3thuan5/hapsing-giliau AS giliau
MAINTAINER i3thuan5
RUN pip install --upgrade https://github.com/i3thuan5/tai5-uan5_gian5-gi2_hok8-bu7/archive/Tacotron%E8%8E%AB%E6%8F%9B%E9%80%9D.zip
RUN python manage.py 匯出Tacotron格式資料 台語 王秀容 /opt/giliau



FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime

RUN apt-get update && \
  apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools wget git vim

RUN git clone https://github.com/fatchord/WaveRNN.git
WORKDIR /WaveRNN

RUN pip install -r requirements.txt

COPY --from=giliau /opt/giliau/taioanoe Taioanoe

COPY hparams.py preprocess.py ./
RUN python preprocess.py
RUN python train.py --model='Tacotron-2'


