FROM pytorch/pytorch:nightly-devel-cuda10.0-cudnn7
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LANG C.UTF-8

RUN git clone https://github.com/NVIDIA/apex /apex/
WORKDIR /apex/
RUN pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" .

WORKDIR /workspace
RUN git clone https://github.com/NVIDIA/tacotron2.git
WORKDIR tacotron2
RUN sed 's/^tensorflow$/tensorflow<1.11/g' -i requirements.txt
RUN pip install -r requirements.txt

