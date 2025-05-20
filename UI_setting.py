# app.py
import gradio as gr
from backend import ZhenHuanQA
import time
import re
from typing import Dict, Any

# 初始化问答系统
qa_system = ZhenHuanQA()

# 自定义CSS（修复版）
custom_css = """
#chatbot {
    min-height: 500px;
    font-family: "Microsoft YaHei", sans-serif;
}
.message.user {
    background: #f0f7ff !important;
    border-radius: 15px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}
.message.bot {
    background: #f8f8f8 !important;
    border-radius: 15px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}
.dark .message.user {
    background: #2a3b4d !important;
}
.dark .message.bot {
    background: #3a4b5d !important;
}
#send-btn {
    background: #4CAF50 !important;
    color: white !important;
    margin-left: 5px !important;
}
#clear-btn {
    background: #f44336 !important;
    color: white !important;
}
.response-content {
    white-space: pre-wrap;
    line-height: 1.7;
    font-size: 15px;
}
.sources-panel {
    margin-top: 15px;
    border-top: 1px dashed #ccc;
    padding-top: 10px;
}
.source-item {
    background: rgba(76, 175, 80, 0.1);
    padding: 8px 12px;
    margin: 8px 0;
    border-radius: 5px;
    font-size: 14px;
}
.dark .source-item {
    background: rgba(104, 211, 145, 0.1) !important;
}
.processing-time {
    color: #888;
    font-size: 12px;
    text-align: right;
    margin-top: 10px;
}
"""


def format_response(raw_response: Dict[str, Any]) -> str:
    """格式化响应为HTML内容"""
    answer = raw_response.get("answer", "未能获取回答内容").strip()
    answer = re.sub(r'回禀主子[：:]?', '🧙‍♀️ <b>嬷嬷回禀</b>：', answer)
    answer = re.sub(r'\n{2,}', '<br><br>', answer)

    sources_html = ""
    if raw_response.get("sources"):
        sources = raw_response["sources"]
        sources_html = "<div class='sources-panel'>"
        sources_html += "<details><summary>📚 <b>剧情来源</b></summary>"
        for i, src in enumerate(sources, 1):
            episode = f"第{src.get('episode', '?')}集"
            scene = src.get('scene', '未知场景')
            content = src.get('content', '内容缺失').replace('\n', '<br>')

            sources_html += f"""
            <div class='source-item'>
                <b>{i}. {episode}·{scene}</b><br>
                {content[:200]}{'...' if len(content) > 200 else ''}
            </div>
            """
        sources_html += "</details></div>"

    return f"""
    <div class='response-content'>
        {answer}
        {sources_html}
    </div>
    """


def respond(message: str, chat_history: list) -> tuple:
    if not message.strip():
        return "", chat_history

    start_time = time.time()

    try:
        enhanced_prompt = f"""
        你是一位电视剧《甄嬛传》中的资深嬷嬷，请按以下要求回答：
        1. 分析需基于《甄嬛传》1-10集剧情原文；剧本是主要以对话形式呈现，格式为“说话人：台词和观点”，请正确理解
        2. 回答需要根据《甄嬛传》1-10集de 人物对话和场景
        3. 分析人物关系要结合事件
        4. 回复保持古风语气

        问题：{message}
        """

        raw_response = qa_system.ask(enhanced_prompt)
        formatted_response = format_response(raw_response)
        process_time = time.time() - start_time
        time_html = f"<div class='processing-time'>⏱️ 处理耗时: {process_time:.2f}秒</div>"
        full_response = f"{formatted_response}{time_html}"

    except Exception as e:
        full_response = f"""
        <div class='response-content'>
            ❌ <b>处理出错</b><br>
            {str(e)}<br>
            请主子换个问法或稍后再试~
        </div>
        """

    chat_history.append((message, full_response))
    return "", chat_history


with gr.Blocks(css=custom_css, theme=gr.themes.Default()) as demo:
    gr.Markdown("""
    <div style="text-align: center;">
        <h1>《甄嬛传》剧情问答</h1>
        <p>本宫执掌后宫事，娘娘们想问什么？</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                elem_id="chatbot",
                bubble_full_width=True,
                height=550,
                render_markdown=True,
                show_copy_button=True
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="例：甄嬛第一次见皇上是在哪一集？",
                    lines=2,
                    max_lines=5,
                    label="御前问话",
                    container=False,
                    autofocus=True
                )
                submit_btn = gr.Button("传话", elem_id="send-btn")
            clear_btn = gr.Button("清空对话", elem_id="clear-btn")

        with gr.Column(scale=1):
            gr.Examples(
                examples=[
                    "甄嬛入宫的具体过程是怎样的？",
                    "分析华妃与皇后的三次正面冲突",
                    "第一集有哪些重要场景？按顺序说明"
                ],
                inputs=msg,
                label="示例问题",
                examples_per_page=5
            )

    msg.submit(respond, [msg, chatbot], [msg, chatbot], queue=True)
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot], queue=True)
    clear_btn.click(lambda: ([], []), outputs=[chatbot, msg], queue=False)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )