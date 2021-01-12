# PKU第二波出入校自动报备

# Dependency

```
pip3 install requests
```

# Usage

```
➜ python3 submitter.py -h
usage: submitter.py [-h] --gate GATE --email EMAIL --phone PHONE --reason REASON
               --desc DESC --street STREET --route ROUTE --file FILE
               --file-type FILE_TYPE [--wechat-key WECHAT_KEY]

自动出入校备案

optional arguments:
  -h, --help            show this help message and exit
  --gate GATE           从哪里进校，如东南门，不知道门叫什么哪个上去看一眼
  --email EMAIL         邮箱
  --phone PHONE         电话
  --reason REASON       出入校事由：就业、学业、科研、就医、寒假离校返乡，五选一别写错了
  --desc DESC           出入校具体事项
  --street STREET       要去的街道，脚本默认海淀区，要改的自己抓包改
  --route ROUTE         行动轨迹
  --file FILE           证明文件
  --file-type FILE_TYPE
                        证明文件类型：健康宝写1，导师同意书写2，建议搞一个导师同意书因为健康宝【可能】要每天截图
  --wechat-key WECHAT_KEY
                        微信推送key，在 http://sc.ftqq.com/3.version 获取，可以妹有

Add environment variable before you use! PKU_USERNAME=学号 PKU_PASSWORD=密码
python3 submitter.py balabala
```

example:

```sh
PKU_USERNAME=1800091828 PKU_PASSWORD=5ecRe7_P4ssw0rd python3 submitter.py \
    --gate "东南门" \
    --email "xxx@pku.edu.cn" \
    --phone "13100000000" \
    --reason "科研" \
    --street "燕园街道" \
    --route "北大-物院-北大" \
    --desc "去实验室" \
    --file "./photo.jpeg" \
    --file-type 1 \
    --wechat-key "xxxxxxxx"
```