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
COPY taioanoe.py .
RUN python taioanoe.py

