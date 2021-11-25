FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime

RUN apt-get update && \
  apt-get install -y git vim-tiny \
    libsndfile1 # librosa output

RUN git clone https://github.com/i3thuan5/WaveRNN.git /WaveRNN
WORKDIR /WaveRNN

ENV LANG C.UTF-8
RUN pip install -r requirements.txt
RUN pip install https://github.com/i3thuan5/tai5-uan5_gian5-gi2_kang1-ku7/archive/master.zip

RUN pip install flask gunicorn
COPY gen_tacotron.py suisiann.py

CMD gunicorn \
  -b 0.0.0.0:5000 \
  --timeout 60 \
  --log-level debug \
  suisiann:app
