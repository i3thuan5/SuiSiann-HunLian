FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
  apt-get install --no-install-recommends -y git \
    libsndfile1 ffmpeg # librosa output, tsuan mp3

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN git clone https://github.com/i3thuan5/WaveRNN.git /WaveRNN
WORKDIR /WaveRNN

ENV LANG C.UTF-8
COPY suisiann.py ./

ENV GUNICORN_TIMEOUT 60
ENV GPU_CONCURRENCY 1

EXPOSE 8000

CMD gunicorn \
  -b 0.0.0.0:8000 \
  --timeout ${GUNICORN_TIMEOUT} \
  --workers 1 \
  -k uvicorn.workers.UvicornWorker \
  --log-level info \
  suisiann:app
