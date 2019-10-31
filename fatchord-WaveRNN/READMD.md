# WaveRNN
自 https://github.com/fatchord/WaveRNN 來訓練。

## 需要
- dobi

## 步
1. 先掠 [SuiSiann-Dataset](https://suisiann-dataset.ithuan.tw/)
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
