# WaveRNN
自 https://github.com/fatchord/WaveRNN 來訓練。

## 安
- [dobi](https://github.com/dnephin/dobi)
- [docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
- [docker-compose](https://docs.docker.com/compose/install/)
- 設定docker權限`sudo usermod -aG docker $USER`

## 步
1. 先用`time dobi liah-giliau`，會掠 [SuiSiann-Dataset](https://suisiann-dataset.ithuan.tw/)，掠好會生做按呢
```
.
├── 0.2
│   ├── ImTong
│   │   ├── SuiSiann_0001.wav
│   │   ├── SuiSiann_0002.wav
│   │   ├── SuiSiann_0003.wav
│   │   ├── SuiSiann_0004.wav
│   │   ├── SuiSiann_0005.wav
│   │    ...
│   └── SuiSiann.csv
├── dobi.yaml
├── Dockerfile
...
```
2. `time dobi tsuan-pianma`，wave downsample 閣降做 16bits，上尾合成較緊
3. `time dobi preprocess-tacotron`，準備tactorn格式。
4. `time dobi tacotron`，訓練Tacotron模型。若是tī tactorn訓練中，欲產生gta檔案，走`dobi tacotron-gta`。
5. `time dobi preprocess-wavernn`，照gta檔案，產生wavernn需要ê`dataset.pkl`
6. `time dobi wavernn`，訓練WaveRNN模型
7. `time dobi huatsiann`，合成語句

#### Pau--khi-lai
```
time dobi hokbu-khuanking
# GPU
docker run --rm -ti -e CUDA_VISIBLE_DEVICES=1 -v `pwd`/kiatko:/kiatko -p 5000:5000 i3thuan5/suisiann-wavernn:SuiSiann-WaveRNN-HokBu-fafoy
# CPU
docker run --rm -ti -e FORCE_CPU=True -v `pwd`/kiatko:/kiatko -p 5000:5000 i3thuan5/suisiann-wavernn:SuiSiann-WaveRNN-HokBu-fafoy
```

##### Tshi(舊)
Python
```python
from http.client import HTTPConnection
from urllib.parse import urlencode

taiBun='tak10-ke7 tsə2-hue1 lai7 tsʰit8-tʰə5 !'
參數 = urlencode({
    'taibun': taiBun,
    'sootsai': 'taiBun/tshi.wav',
})
headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"
}
it_conn = HTTPConnection('hapsing', port=5000)
it_conn.request("POST", '/', 參數, headers)
it_conn.getresponse().read()
```
