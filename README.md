# MGD-Helper

基于 20-20-20 护眼原则的低侵入性定时提醒工具。

默认设置：每隔 20 分钟提醒，短休 4 分钟，每 3 轮短休后长休 13 分钟。

## 特性

- **弹窗模式**：到时间弹出对话框，倒计时结束后可关闭，支持填写感想笔记（可选）和推迟
- **纯托盘通知模式**：仅显示系统托盘通知，无弹窗、无声音，适合开会等场景
- **暂停弹窗**：临时切换到托盘通知模式（15/30/60/90 分钟），适合需要专注时
- **可视化配置界面**：通过托盘菜单 → 设置可调整所有参数，保存即时生效
- **独立音频开关**：提示音、BGM、警报三项可独立开启/关闭
- **紧凑 UI**：深色主题低调用设计，减少被他人注意的可能
- **无法轻易关闭**：托盘菜单无退出选项，确保护眼计划持续执行

## 配置

配置文件路径：`~/.config/mgd-helper.json`

首次运行自动生成默认配置。可通过托盘菜单 → 设置进行可视化编辑，无需手动改文件。

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `mention_duration` | 20 | 提醒间隔（分钟） |
| `short_mention_time` | 4 | 短休时长（分钟） |
| `long_mention_time` | 13 | 长休时长（分钟） |
| `long_mention_rounds` | 3 | 每 N 轮短休触发一次长休 |
| `delay_time` | 5 | 推迟时间（分钟） |
| `mode` | `popup` | 默认模式：`popup`（弹窗）/ `tray_only`（托盘通知） |
| `popup_style` | `compact` | 弹窗样式：`compact` / `standard` |
| `dingdong_enabled` | `true` | 弹窗提示音 |
| `bgm_enabled` | `false` | 休息背景音乐 |
| `alarm_enabled` | `true` | 超时警报 |

日志路径：`~/.config/mgd-helper-log.jsonl`

## 编译

```sh
pyinstaller.exe main.py --add-data 'asset/*:asset/' --icon 'asset/icon.ico' --noconsole --onefile --name MGD-Helper
```

## 依赖

- Python 3.10+
- PyQt5
- Pydantic
