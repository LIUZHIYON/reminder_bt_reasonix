# 提醒行为树 — Reminder BT

基于 BehaviorTree.CPP v4 + Python BT 引擎的提醒系统，支持 Web 端创建提醒、到时间自动 doubao TTS 语音播报。

## 快速开始

### 1. 部署到板子

```bash
ssh cat@192.168.1.107
mkdir -p ~/reminder_bt/board_data /tmp/reminder_audio
# 从 PC 上传核心文件
scp bt_engine.py reminder_nodes.py reminder_tree.py groot2_server.py cat@192.168.1.107:~/reminder_bt/
```

### 2. 安装依赖

```bash
pip3 install pyzmq msgpack edge-tts --user
```

### 3. 启动行为树服务器

```bash
cd ~/reminder_bt
nohup python3 -u groot2_server.py --port 1669 --pub-port 1670 \
    --data-dir ~/reminder_bt/board_data \
    --audio-dir /tmp/reminder_audio \
    > /tmp/reminder_bt.log 2>&1 &
```

### 4. 启动 Web API

```bash
cd ~/reminder_bt
nohup python3 -u web.py > /tmp/web.log 2>&1 &
```

### 5. 启动 PC 播放器（Windows）

```bash
python pc_player.py
```

---

## 测试指令

### 立即触发

```bash
curl -s -X POST http://127.0.0.1:8080/api/reminders \
  -H 'Content-Type: application/json' \
  -d '{"title":"小明","content":"该吃饭啦","trigger_time":"2000-01-01T00:00:00"}'
```

### 定时触发（2分钟后）

```bash
curl -s -X POST http://127.0.0.1:8080/api/reminders \
  -H 'Content-Type: application/json' \
  -d '{"title":"定时测试","content":"到点了","trigger_time":"2026-06-27T14:05:00"}'
```

### 查看提醒列表

```bash
curl -s http://127.0.0.1:8080/api/reminders | python3 -m json.tool
```

### 查看行为树状态（BehaviorTreeMonitor）

连接到 `192.168.1.107:1669`

### 测试豆包 TTS

```bash
source /opt/ros/humble/setup.bash
ros2 action send_goal /voice/speak robot_voice_bridge/action/Speak "{text: '测试语音播放'}"
```

---

## 架构

```
Web/curl -> :8080 API -> reminders.json
                          -> groot2_server (1669)
                               -> BehaviorTree (13 nodes)
                                  ReactiveSequence
                                  +-- CheckTime
                                  +-- Sequence
                                      +-- BuildTtsText
                                      +-- GenerateTTS -> voice_bridge -> doubao TTS
                                      +-- PlaySpeaker
                                      +-- SavePersistence -> board_data/*.json
                                      +-- PublishStatus
                          -> pc_player.py -> PC 喇叭
```

## 端口

| 端口 | 服务 |
|------|------|
| 1669 | BehaviorTree Groot2 ZMQ |
| 1670 | BehaviorTree PUB |
| 8080 | Web API |

## 文件说明

| 文件 | 说明 |
|------|------|
| groot2_server.py | 主程序：加载提醒、运行行为树、ZMQ 监控 |
| bt_engine.py | 行为树引擎 |
| reminder_nodes.py | 6 个自定义 BT 节点 |
| reminder_tree.py | 行为树结构定义 |
| web.py | Web API 服务器 |
| pc_player.py | PC 端语音播放器 |
| pc_frontend/ | PC 本地前端 |