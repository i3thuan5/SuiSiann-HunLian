# WaveRNN
自 https://github.com/fatchord/WaveRNN 來訓練。

## 需要
- dobi
- sox

## 步
1. 先掠 [SuiSiann-Dataset](https://suisiann-dataset.ithuan.tw/)，轉做對應頻率
```
export PANPUN=0.2
mkdir -p tsiamsi-${PANPUN}/ImTong/
find ${PANPUN} -name '*wav' -exec sox {} -b 16 -c 1 -r 16k tsiamsi-{} \;
mv tsiamsi-${PANPUN} ${PANPUN}-22050
cp ${PANPUN}/*csv ${PANPUN}-22050
ln -s ${PANPUN}-22050 giliau
```
2. `dobi preprocess`
3. `dobi tacotron`
4. `dobi tacotron-gta`
5. `dobi wavernn`

### 提掉大檔
Tacotron 尾仔ê GTA ê留較短ê檔，所以ē-tàng整理出來予WaveRNN用
```
ls data/gta/ | sed 's/.npy//g' | tee gta_u
find data/mel/ -type f | grep -v -f gta_u  | xargs rm 
find data/quant/ -type f | grep -v -f gta_u  | xargs rm 
find 0.1-22050-gta/ImTong/ -type f | grep -v -f gta_u  | xargs rm 
```


#### Pau--khi-lai
```
dobi hokbu-khuanking
docker run --rm -ti -e CUDA_VISIBLE_DEVICES=1 -v `pwd`/kiatko:/kiatko -p 5000:5000 suisiann-wavernn:SuiSiann-WaveRNN-HokBu-fafoy
```

##### Tshi
Python
```python
from http.client import HTTPConnection
from urllib.parse import urlencode

taiBun='tak10-ke7 tsə2-hue1 lai7 tsʰit8-tʰə5 !'
參數 = urlencode({
    'taibun': taiBun,
})
headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"
}
it_conn = HTTPConnection('192.168.33.20', port=5000)
it_conn.request("POST", '/', 參數, headers)
it_conn.getresponse().read()
```
