#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_qr.py —— 生成问卷二维码（屏幕版 + 印刷版）

用法：
    python make_qr.py "https://www.wjx.cn/vm/xxxxx.aspx"
    python make_qr.py "https://xxx.netlify.app/quiz.html" --dir D:\\out

产出（默认写到脚本所在目录）：
    qrcode.png         492px 左右，投屏/手机展示/放进 #host 主持人页
    qrcode_print.png   高分辨率，可打印桌牌、A4 海报（容错等级 H，最抗磨损）
"""
import argparse
import os
import sys

try:
    import segno
except ImportError:
    sys.exit("缺少 segno 库，请先运行：python -m pip install segno")

HERE = os.path.dirname(os.path.abspath(__file__))


def render(url: str, out_dir: str = HERE) -> tuple[str, str]:
    """把 url 渲染成两张 PNG，返回 (屏幕版路径, 印刷版路径)。"""
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("链接必须以 http:// 或 https:// 开头")

    qr = segno.make(url, error="h")          # H 级容错，最抗打印磨损与反光
    os.makedirs(out_dir, exist_ok=True)

    screen = os.path.join(out_dir, "qrcode.png")
    printable = os.path.join(out_dir, "qrcode_print.png")

    qr.save(screen, scale=12, border=4, dark="#071018", light="#ffffff")
    qr.save(printable, scale=40, border=4, dark="#000000", light="#ffffff")
    return screen, printable


def main() -> None:
    ap = argparse.ArgumentParser(description="生成问卷二维码")
    ap.add_argument("url", help="问卷链接（含 https://）")
    ap.add_argument("--dir", default=HERE, help="输出目录，默认脚本所在目录")
    args = ap.parse_args()

    try:
        screen, printable = render(args.url, args.dir)
    except ValueError as exc:
        sys.exit(str(exc))

    print(f"链接    : {args.url.strip()}")
    print(f"屏幕版  : {screen}")
    print(f"印刷版  : {printable}")
    print("提示    : 把 qrcode.png 放在 quiz.html 同目录，主持人模式 #host 会自动显示。")


if __name__ == "__main__":
    main()
