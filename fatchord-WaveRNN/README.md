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

## Tshi
### Curl
#### Get
```bash
time curl \
  'localhost:5000/?taibun=Ta%CC%8Dk-ke%20ts%C3%B2-hu%C3%A9%20l%C3%A2i%20tshit-th%C3%B4%20!'
```
#### Post
```
time curl -i -X POST \
  -H "Content-type: application/x-www-form-urlencoded" \
  -H "Accept: text/plain" \
  -d 'taibun=Ta̍k-ke tsò-hué lâi tshit-thô !' \
  localhost:5000
```
### Python3
```python
from http.client import HTTPConnection
from urllib.parse import urlencode

taiBun = 'Ta̍k-ke tsò-hué lâi tshit-thô !'
參數 = urlencode({
    'taibun': taiBun,
})
headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"
}
it_conn = HTTPConnection('localhost', port=5000)
it_conn.request("POST", '/', 參數, headers)
it_conn.getresponse().read()
```
