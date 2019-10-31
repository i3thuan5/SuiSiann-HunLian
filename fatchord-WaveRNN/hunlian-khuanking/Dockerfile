FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime

RUN apt-get update && \
  apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools git vim-tiny

RUN git clone https://github.com/fatchord/WaveRNN.git /WaveRNN
WORKDIR /WaveRNN

ENV LANG C.UTF-8
RUN pip install -r requirements.txt

