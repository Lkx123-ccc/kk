#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
serve.py —— 现场一键开服：自动识别本机 IP、自动按该 IP 重新生成二维码、自动打开主持人页。

用法：
    双击 serve.bat（推荐，ASCII 启动器，不会有编码问题）
    或命令行：python serve.py
    自检（不开服务，只看识别到的地址与二维码）：python serve.py --check
"""
import os
import socket
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

PORT = 8000
FALLBACK_PORTS = (8080, 8081, 8008)


def lan_ip() -> str:
    """取默认路由所在网卡的 IPv4；失败则回环。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))   # 不发包，只用于选出口网卡
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):          # 只留一行简洁日志
        sys.stderr.write("  · %s\n" % (fmt % args))


def banner(ip: str, port: int) -> str:
    url = f"http://{ip}:{port}/quiz.html"
    return f"""
============================================
 赛博算命 · 现场开服 + 自动出码
============================================

  同学扫码地址 : {url}
  主持人页面   : {url}#host

  二维码已按上面地址写入：
    qrcode.png        投屏 / 手机展示用
    qrcode_print.png  打印桌牌、A4 海报用

  ---- 让手机真的扫得通，还要满足 ----
  1) 手机与这台电脑连同一个 WiFi 或同一个热点
  2) 校园网常开「客户端隔离」，跨设备访问会失败，改用手机热点最稳
  3) 首次运行被防火墙拦截时，请点「允许访问」；仍不通则用管理员命令行执行：
     netsh advfirewall firewall add rule name="CyberQuiz8000" dir=in action=allow protocol=TCP localport={port}
  4) iPhone 热点最多约 5 台设备、安卓热点约 10 台，人数多请改用公网托管

  按 Ctrl+C 停止服务。
"""


def main() -> None:
    check_only = "--check" in sys.argv
    ip = lan_ip()

    # 1) 按当前 IP 重新生成二维码
    qr_ok = True
    try:
        from make_qr import render
        render(f"http://{ip}:{PORT}/quiz.html", HERE)
    except Exception as exc:                     # noqa: BLE001 - 出码失败不阻止开服
        qr_ok = False
        print(f"[warn] 二维码生成失败：{exc}")

    print(banner(ip, PORT), end="")
    if not qr_ok:
        print("       （二维码未更新，请先 pip install segno）\n")

    if check_only:
        print("  [check] 已跳过启动服务与打开浏览器。\n")
        return

    # 2) 起服务（端口被占用自动换）
    httpd = None
    for port in (PORT,) + FALLBACK_PORTS:
        try:
            httpd = ThreadingHTTPServer(("0.0.0.0", port), QuietHandler)
            if port != PORT:
                print(f"  {PORT} 被占用，改用 {port}，二维码已按新端口重新生成。\n")
                try:
                    from make_qr import render
                    render(f"http://{ip}:{port}/quiz.html", HERE)
                except Exception:            # noqa: BLE001
                    pass
            break
        except OSError:
            continue

    if httpd is None:
        sys.exit("端口全被占用，请关掉占用程序后重试。")

    port = httpd.server_address[1]
    url = f"http://{ip}:{port}/quiz.html"
    try:
        webbrowser.open(url + "#host")
    except Exception:                            # noqa: BLE001
        pass

    print(f"  服务已启动：{url}\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止。")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
