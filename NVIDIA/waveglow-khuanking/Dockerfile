FROM pytorch/pytorch:nightly-devel-cuda10.0-cudnn7
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LANG C.UTF-8

RUN apt-get update -y

RUN pip install numpy scipy matplotlib librosa==0.6.0 'tensorflow<2.0' tensorboardX inflect==0.2.5 Unidecode==1.0.22 jupyter

RUN git clone https://github.com/NVIDIA/apex /apex/
WORKDIR /apex/
RUN pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" .

WORKDIR /workspace
RUN git clone https://github.com/NVIDIA/waveglow.git
RUN cd waveglow
RUN git submodule init; git submodule update
