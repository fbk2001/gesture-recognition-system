# 手势识别系统（Hand Gesture Recognition）

## 项目简介

本项目基于 MediaPipe 和 OpenCV，实现实时手势识别与可视化展示，提供一个带 GUI 的演示程序和一个简单的控制台 demo。

主要功能：
- 使用 MediaPipe Hands 提取手部关键点
- 通过关键点计算手指二维夹角并判断常见手势（如 one、five、three 等）
- GUI 界面用于实时展示摄像头或视频流、识别结果与日志，并支持录制输出到 Video.avi

## 主要文件说明

- `main/gesture_classification.py`：带 PyQt5 GUI 的主程序，包含识别线程、图像显示、日志与开始/停止控制。
- `main/demo.py`：最小化的演示脚本，直接打开摄像头并在窗口中可视化手部关键点，按 ESC 或关闭窗口退出（适合快速验证摄像头与 MediaPipe 是否可用）。
- `main/requirements.txt`：项目 Python 依赖清单，可用于 pip 安装。
- `main/setup.py`：MediaPipe 的打包/构建脚本（仅在需要从源码构建 MediaPipe 或生成 protobuf 时使用）。

## 环境要求

- 操作系统：Windows、Linux 或 macOS（本文示例以 Windows PowerShell 为运行命令）
- 建议 Python 版本：3.8 - 3.10
- 安装 Conda（用于隔离环境）

## 快速搭建（PowerShell）

1) 创建并激活 Conda 环境：

```powershell
conda create -n hand_gesture python=3.8 -y
conda activate hand_gesture
```

2) 在激活的环境中安装 Python 依赖：

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r main/requirements.txt
```

3) 可选：如果需要从源码构建 MediaPipe，需安装 Bazel 与 protoc（protobuf 编译器），这些为系统级工具，不通过 pip 安装。

## 运行方法

1) 运行控制台 demo（快速验证摄像头与 MediaPipe）：

```powershell
python main/demo.py
```

- 打开窗口后会显示实时摄像头画面。
- 按 ESC 键或关闭窗口退出程序。

2) 运行带 GUI 的识别程序：

```powershell
python main/gesture_classification.py
```

- 在界面 "输入路径" 文本框中输入摄像头 ID（例如 `0`）或视频文件路径，然后点击“开始识别”。
- 点击“停止识别”按钮可中断识别线程并安全结束录制。
- 识别的视频帧会保存为当前目录下的 `Video.avi`（默认分辨率及帧率见程序内定义）。

## 常见问题与排查建议

1) 程序启动时出现如下类型的 WARNING：

- `INFO: Created TensorFlow Lite XNNPACK delegate for CPU.`
- `Feedback manager requires a model with a single signature inference. Disabling support for feedback tensors.`

这些多为运行时的警告信息，通常不会阻止程序执行。

2) 程序异常退出，返回代码如 `0xC0000409` 或 `-1073740791`：

- 这类错误通常来自底层本地库（例如 MediaPipe/TF Lite/OpenCV）出现问题。可尝试：
  - 更新或降级 `mediapipe` 与 `opencv-contrib-python`，使两者版本兼容。
  - 先运行 `main/demo.py` 验证基本摄像头与关键点可用，再运行 GUI 程序。
  - 若问题在 GUI 中出现，可在终端查看完整 traceback 和 stderr 信息以定位是 Python 层还是本地扩展崩溃。

3) 运行 `main/setup.py` 报错 `README.md not found` 或 `error: no commands supplied`：

- `setup.py` 为 MediaPipe 的构建脚本，直接执行通常会因为未传入构建/安装命令而显示提示。若只想运行 demo，不需要调用 `setup.py`。
- `README.md` 缺失会触发警告，已在本目录添加 `main/README.md` 可避免该警告。

4) GUI 窗口无法关闭或点击关闭会重启界面：

- GUI 使用线程来处理摄像头和识别，正常关闭窗口或点击“停止识别”时程序会调用线程停止接口并释放摄像头资源。
- 若出现无法关闭的情况，请在运行程序的终端中按 Ctrl+C 强制中断，或在任务管理器结束 Python 进程；然后检查终端输出以定位异常或未捕获的错误。

## 日志与输出

- 实时识别日志会显示在 GUI 左侧的日志区域（`textBrowser_2`）。
- 识别结果会覆盖渲染到画面上，并同时写入日志。
- 录制的输出文件默认为 `Video.avi`（程序退出时会尝试释放并保存文件）。

## 进阶说明（可选）

- 如果需要更稳定或性能更高的部署，考虑：
  - 使用 MediaPipe 的预编译 wheel（与目标平台对应）而非从源码构建。
  - 在 GPU 环境或移动设备上使用 MediaPipe 的 GPU/accelerator 特性（需额外配置）。

## 联系与贡献

若你在使用或改进本项目时遇到问题，欢迎在代码仓库中打开 issue，或将改动以分支/合并请求的方式提交。
