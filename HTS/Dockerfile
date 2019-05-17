FROM i3thuan5/hapsing-giliau
MAINTAINER i3thuan5

RUN apt-get update -qq && \
  apt-get install -y csh libc6-dev-i386 linux-libc-dev gcc-multilib libx11-dev
RUN pip install --upgrade https://github.com/i3thuan5/tai5-uan5_gian5-gi2_hok8-bu7/archive/hts_huetshut_langkue.zip
RUN pip install --upgrade https://github.com/i3thuan5/tai5-uan5_gian5-gi2_kang1-ku7/archive/Siu_imun.zip
RUN python manage.py 訓練HTS 台語 王秀容 

