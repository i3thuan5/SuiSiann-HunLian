# TODO

## 產生 requirements.txt

需要在有 Docker 的環境執行，確保 lock 的版本跟 Dockerfile base image 一致：

```bash
cd fatchord-WaveRNN/hokbu-khuanking

docker run --rm -v "$(pwd)":/work -w /work \
  pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime \
  bash -c "pip install pip-tools && pip-compile requirements.in -o requirements.txt"
```

### Claude prompt

```
幫我用 docker 跑 pip-compile 產生 requirements.txt：

cd fatchord-WaveRNN/hokbu-khuanking
docker run --rm -v "$(pwd)":/work -w /work \
  pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime \
  bash -c "pip install pip-tools && pip-compile requirements.in -o requirements.txt"

跑完後確認 requirements.txt 有產生，然後 commit。
```
