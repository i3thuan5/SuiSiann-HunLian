FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

COPY requirements.in ./
COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get update && \
  apt-get install -y git vim-tiny \
    libsndfile1 ffmpeg # librosa output, tsuan mp3

RUN git clone https://github.com/i3thuan5/WaveRNN.git /WaveRNN
WORKDIR /WaveRNN

ENV LANG C.UTF-8
COPY gen_tacotron.py suisiann.py

ENV GUNICORN_TIMEOUT 60
ENV GUNICORN_WORKERS 6
ENV GUNICORN_MAX_REQUESTS 30
ENV GUNICORN_MAX_REQUESTS_JITTER 10

EXPOSE 5000

CMD gunicorn \
  -b 0.0.0.0:5000 \
  --timeout ${GUNICORN_TIMEOUT} \
  --workers ${GUNICORN_WORKERS} \
  --max-requests ${GUNICORN_MAX_REQUESTS} \
  --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER} \
  --log-level debug \
  suisiann:app
