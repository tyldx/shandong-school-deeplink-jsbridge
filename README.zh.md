# 闪动校园学生端 深链白名单绕过导致 JSBridge 越权调用

[English](README.md)

`com.huachenjie.shandong_school` 8.8.1 (versionCode 26102914) 的漏洞研究与 PoC。

## 文档

| 文件 | 内容 |
|---|---|
| [`REPORT.zh.md`](REPORT.zh.md) | 主报告 |
| [`poc/`](poc/) | PoC 代码 |
| [`tools/md2pdf.py`](tools/md2pdf.py) | Markdown 转 PDF |

## 边界

所有测试均在官方线上 App 中,使用本人注册并控制的测试账号进行;未针对任何第三方账号实施,未获取或使用他人凭证及数据。

局限:仅在 Android 版 8.8.1(Android 17)上测试,iOS 版及其他版本未实测。

## 许可证

[MIT](LICENSE)
