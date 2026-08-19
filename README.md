# 联机视频通话（WebRTC）

预览地址：https://c5d09ee0.sc.monkeycode-ai.online

基于 **Python + 原生 JavaScript（WebRTC）** 的联机视频通话应用。

- 后端：Python 3（`aiohttp` WebSocket 信令服务器），单文件
- 前端：原生 HTML/JS/CSS，`getUserMedia` 采集 + `RTCPeerConnection` 点对点传输，无任何框架
- 支持多人同大厅、在线成员列表、点对点呼叫 / 接听 / 拒绝 / 挂断、摄像头与麦克风独立开关、麦克风输入音量表、本地画面可拖动（正方形，随放随移）与镜像、TURN 中继（NAT 打洞失败时）

## 文件结构

```
videocall/
├── videocall_server.py   # 后端：WebSocket 信令服务器
├── index.html            # 前端：页面 + WebRTC 客户端逻辑
└── README.md             # 本文档
```

## 依赖

| 项 | 要求 |
|----|------|
| Python | 3.7+ |
| aiohttp | `pip install aiohttp`（WebSocket 信令） |
| 浏览器 | 支持 WebRTC（Chrome / Edge / Safari / 安卓等），需 https 或 localhost 访问 |
| TURN（可选） | coturn（仅当双方 NAT 打洞失败时需要） |

## 启动

```bash
# 1. 安装依赖
pip install aiohttp

# 2. 启动服务器（默认 0.0.0.0:8080）
cd videocall
python videocall_server.py
```

启动后控制台显示 `视频通话服务器已启动: http://0.0.0.0:8080/?name=昵称`。

## 使用

1. 用浏览器打开 `http://服务器IP:8080/?name=你的昵称`（**必须 https 或 localhost，否则浏览器禁用摄像头和 WebRTC**）
2. 页面自动进入大厅，右侧显示**在线成员列表**
3. 点某个成员的"**呼叫**" → 对方弹出"邀请你视频通话"→ 对方点"**接听**"即建立通话
4. 通话中可随时开关摄像头 / 麦克风、挂断；麦克风音量条显示在本地小窗上方

### URL 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `name` | 昵称（显示在成员列表） | `?name=小明` |
| `turn` | TURN 服务器地址（可选，打洞失败时用） | `?turn=1.2.3.4:3478` |
| `user` / `pass` | TURN 账号密码（与 `turn` 一起用） | `&user=calluser&pass=xxx` |

完整示例（带 TURN）：

```
https://你的域名:8080/?name=小明&turn=1.2.3.4:3478&user=calluser&pass=密码
```

两端必须进**同一个页面地址**（同名参数），即可在成员列表中互呼。

### 部署 TURN（可选，解决 NAT 打洞失败）

```bash
apt-get install -y coturn
sed -i 's/#ENABLED=1/ENABLED=1/' /etc/default/coturn
cat >> /etc/turnserver.conf <<'EOF'
listening-port=3478
fingerprint
lt-cred-mech
realm=你的域名
user=calluser:换成纯ASCII密码
no-cli
EOF
systemctl restart coturn
```

云安全组放行：TCP+UDP 3478、UDP 49152-65535。前端访问时带 `?turn=IP:3478&user=calluser&pass=密码` 即自动启用。

## 说明与注意

- 摄像头 / 麦克风需要用户授权，授权弹窗记得点"允许"
- 移动端自动播放限制：收到对方画面后，点一下屏幕即可恢复远端声音
- 没有摄像头/麦克风的设备也可进入通话，只是无法发送对应媒体
- 通话画面默认点对点直连，不经过服务器；TURN 只在打洞失败时中转
- 信令服务器仅转发文字信令（SDP/ICE），不承载音视频
