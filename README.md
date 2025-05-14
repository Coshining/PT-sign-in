# PT-sign-in

> PT 站 自动签到脚本

## 使用

```
ql repo https://github.com/KunCheng-He/icc2022-sign-in.git "icc2022.py" "" "sendNotify"
```

青龙面板新增环境变量 `PT_SIGN_CONFIG`，可以根据 `example.json` 格式填写多条PT站配置。

环境变量添加完成后，回到 `订阅管理` 点击运行，就会自动添加定时任务。

## 致谢

- 本项目大部分代码参考自 [KunCheng-He/icc2022-sign-in](https://github.com/KunCheng-He/icc2022-sign-in)，感谢
