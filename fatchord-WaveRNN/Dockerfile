FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-runtime

RUN apt-get update && \
  apt-get install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools git vim-tiny

RUN git clone https://github.com/fatchord/WaveRNN.git /WaveRNN
WORKDIR /WaveRNN

ENV LANG C.UTF-8
RUN pip install -r requirements.txt
RUN pip install https://github.com/i3thuan5/tai5-uan5_gian5-gi2_kang1-ku7/archive/pian-tiau.zip
RUN pip install --upgrade librosa
RUN git pull # 20191125

RUN pip install flask gunicorn
COPY tshamsoo/hparams.py .
COPY tshamsoo/text_init.py utils/text/__init__.py
COPY tshamsoo/symbols.py utils/text/symbols.py
COPY checkpoints/suisiann_lsa_smooth_attention.tacotron/latest* checkpoints/suisiann_lsa_smooth_attention.tacotron/
COPY checkpoints/suisiann_raw.wavernn/latest* checkpoints/suisiann_raw.wavernn/
COPY hokbu-khuanking/gen_tacotron.py suisiann.py
CMD gunicorn \
  -b 0.0.0.0:5000 \
  --timeout 60 \
  --log-level debug \
  suisiann:app


