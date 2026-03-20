from ..utils import *
import markdown2
from playwright.async_api import async_playwright

async def md_to_image(md_text, width=800):
    html_body = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "task_list"])

    config = {
        "line_height": "1.8",
        "font_size": "16px",
        "container_padding": "50px",
        "background": "linear-gradient(135deg, #f5f7fa 0%, #AEA0B3 100%)", 
        "card_bg": "rgba(255, 255, 255, 1)",
        "text_color": "#0f151b"
    }

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script>
            window.mathjaxFinished = false;
            window.MathJax = {{
                tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$']] }},
                startup: {{ pageReady: () => MathJax.startup.defaultPageReady().then(() => {{ window.mathjaxFinished = true; }}) }}
            }};
        </script>
        <script src="https://unpkg.zhimg.com/mathjax@4.1.0/tex-chtml.js" async></script>
        <style>
            body {{ 
                margin: 0;
                padding: 60px 20px;
                display: flex; 
                justify-content: center; 
                background: {config['background']}; 
                min-height: 100vh;
                font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
            }}

            #container {{ 
                background: {config['card_bg']}; 
                padding: {config['container_padding']}; 
                border-radius: 16px; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.15); 
                width: {width}px; 
                color: {config['text_color']};
                line-height: {config['line_height']};
                font-size: {config['font_size']};
            }}

            p {{ margin-bottom: 1.5em; }}
            h1, h2, h3 {{ margin-top: 1.5em; margin-bottom: 0.8em; color: #1a1a1a; }}
            pre {{ 
                background: #282c34; color: #abb2bf; padding: 20px; 
                border-radius: 8px; overflow-x: auto; line-height: 1.4;
            }}
            code {{ background: rgba(0,0,0,0.05); padding: 2px 5px; border-radius: 4px; font-family: 'Fira Code', monospace; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #dfe2e5; padding: 12px; text-align: left; }}
            th {{ background: #f6f8fa; }}
        </style>
    </head>
    <body>
        <div id="container">{html_body}</div>
    </body>
    </html>
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(device_scale_factor=2)
        page = await context.new_page()
        await page.set_content(full_html, wait_until="domcontentloaded")


        try:
            await page.wait_for_function("window.mathjaxFinished === true", timeout=10000)
        except:
            pass 
        
        await page.wait_for_timeout(500)

        container = page.locator("#container")
        gen_image = await container.screenshot()
        await browser.close()
    
    return gen_image