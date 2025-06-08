import asyncio  # <--- 【第1处改动】导入标准库 asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyppeteer
import markdown
import oss2
from datetime import datetime

# --- 配置信息 (无变动) ---
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET', 'YOUR_ACCESS_KEY_SECRET')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME', 'YOUR_BUCKET_NAME')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')
OSS_BUCKET_URL = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}"

app = FastAPI()
auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

class CardRequest(BaseModel):
    main_content: str

def create_html_content(text_with_markdown: str) -> str:
    # HTML部分保持不变，是正确的
    html_fragment = markdown.markdown(text_with_markdown)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>峰言峰语卡片</title>
        <link rel="stylesheet" href="https://unpkg.com/heti/umd/heti.min.css">
        <style>
            @font-face {{ font-family: 'GenWanMin TW TTF'; }}
            @font-face {{ font-family: 'Yozai'; }}
            body, html {{
                margin: 0; padding: 0; height: 100%; display: flex;
                justify-content: center; align-items: center; background-color: #f0f0f0;
                font-family: 'Siyuan', sans-serif;
            }}
            .card {{
                width: 300px; min-height: 400px; background: linear-gradient(135deg, #e6f2ff 0%, #ffffff 100%);
                padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column;
            }}
            .content {{ background: linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%); border-radius: 15px; padding: 20px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); flex-grow: 1; display: flex; flex-direction: column; position: relative; }}
            .header {{ display: flex; align-items: center; margin-bottom: 15px; }}
            .avatar-container {{ width: 40px; height: 40px; border-radius: 50%; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-right: 10px; position: relative; }}
            .avatar-inner-ring {{ position: absolute; top: 2px; left: 2px; right: 2px; bottom: 2px; border-radius: 50%; background: linear-gradient(45deg, #ff00ff, #00ff00, #0000ff, #ff0000); animation: gradient 5s ease infinite; z-index: 1; }}
            .avatar-content {{ position: relative; width: calc(100% - 4px); height: calc(100% - 4px); margin: 2px; border-radius: 50%; overflow: hidden; z-index: 2; }}
            .avatar {{ width: 100%; height: 100%; object-fit: cover; }}
            .kol-name {{ font-family: 'GenWanMin TW TTF', sans-serif; font-weight: bold; font-size: 14px; color: #333; }}
            .main-content {{ text-align: left; flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; overflow: hidden; }}
            .main-title {{ font-family: 'Yozai', sans-serif; font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
            .sub-title {{ font-family: 'Yozai', sans-serif; font-size: 14px; line-height: 1.6; flex-grow: 1; }}
            .footer {{ font-family: 'GenWanMin TW TTF', sans-serif; font-size: 11px; color: #666; text-align: right; margin-top: 10px; }}
            .decorative-icon {{ position: absolute; top: 15px; right: 15px; width: 20px; height: 20px; background-color: #a0c4ff; border-radius: 50%; }}
            strong {{ font-weight: 900; color: #0056b3; }}
            @keyframes gradient {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        </style>
    </head>
    <body>
        <div class="card">
             <div class="content heti">
                <div class="decorative-icon"></div>
                <div class="header">
                    <div class="avatar-container">
                        <div class="avatar-inner-ring"></div>
                        <div class="avatar-content"><img src="https://telegraph-image-els.pages.dev/file/30d8991bb448e10c5b795.jpg" alt="峰哥亡命天涯" class="avatar"></div>
                    </div>
                    <div class="kol-name">@峰哥亡命天涯</div>
                </div>
                <div class="main-content">
                    <div class="main-title">峰言·峰语</div>
                    <div class="sub-title">{html_fragment}</div>
                </div>
                <div class="footer">小红书 | 内容创作</div>
            </div>
        </div>
        <script src="https://unpkg.com/heti/umd/heti-addon.min.js"></script>
        <script>
            const heti = new Heti('.heti');
            heti.autoSpacing();
        </script>
    </body>
    </html>
    """
    return html_template

@app.post("/generate")
async def generate_card(request: CardRequest):
    html_content = create_html_content(request.main_content)
    screenshot_path = "/tmp/card.png"

    try:
        browser = await pyppeteer.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        
        # 步骤1：只设置HTML内容
        await page.setContent(html_content)

        # 步骤2：使用标准库 asyncio.sleep 进行强制等待，不再依赖 pyppeteer 的任何等待函数
        await asyncio.sleep(2)  # <--- 【第2处改动】使用 guaranteed-to-work 的方法

        # 步骤3：等待字体渲染完毕
        await page.evaluate('document.fonts.ready')

        # 步骤4：后续流程不变
        dimensions = await page.evaluate('''() => {
            const card = document.querySelector('.card');
            return { 'width': card.offsetWidth, 'height': card.offsetHeight }
        }''')
        
        await page.setViewport({ 'width': dimensions['width'], 'height': dimensions['height'], 'deviceScaleFactor': 2 })
        await page.screenshot({'path': screenshot_path, 'type': 'png', 'fullPage': True})
        await browser.close()

        file_name = f"feng_card_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        bucket.put_object_from_file(file_name, screenshot_path)
        os.remove(screenshot_path)
        
        return {"image_url": f"{OSS_BUCKET_URL}/{file_name}"}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Card Generation Service is running."}