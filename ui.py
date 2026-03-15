import gradio as gr
from langchain_core.messages import HumanMessage
import uuid

# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_text(text: str) -> str:
    return (text
        .replace('`', "'")
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

def format_video_card(video: dict) -> str:
    score = video.get("score", 0) or 0
    level = sanitize_text(video.get("detected_level", "?"))
    for_students = "Student-friendly" if video.get("for_students") else "Native content"
    cc = video.get("CC", False)
    url = f"https://www.youtube.com/watch?v={video.get('video_id', '')}"
    views = video.get("views", 0)
    views_str = f"{views:,}" if views else "?"
    title = sanitize_text(video.get('title', 'Unknown'))
    channel = sanitize_text(video.get('channel_title', ''))
    explanation = sanitize_text(video.get('score_explanation', ''))
    explanation_short = explanation[:220] + ('...' if len(explanation) > 220 else '')

    if score >= 70:
        score_bg, score_color, score_border = "#dcfce7", "#15803d", "#86efac"
    elif score >= 40:
        score_bg, score_color, score_border = "#fef9c3", "#a16207", "#fde047"
    else:
        score_bg, score_color, score_border = "#fee2e2", "#b91c1c", "#fca5a5"

    cc_badge = (
        '<span style="background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;'
        'border-radius:4px;padding:1px 6px;font-size:11px;">CC</span>'
        if cc else ""
    )

    return f"""
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;
        padding:14px;margin:6px 0;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;">
            <a href="{url}" target="_blank"
                style="color:#111827;font-size:13px;font-weight:600;
                text-decoration:none;line-height:1.4;flex:1;"
                onmouseover="this.style.color='#d97706'"
                onmouseout="this.style.color='#111827'">
                {title}
            </a>
            <span style="background:{score_bg};color:{score_color};
                border:1px solid {score_border};border-radius:20px;
                padding:1px 8px;font-size:11px;font-weight:700;white-space:nowrap;">
                {score}/100
            </span>
        </div>
        <div style="color:#6b7280;font-size:11px;margin-top:4px;">
            {channel} &middot; {views_str} views
        </div>
        <div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:8px;">
            <span style="background:#f3f4f6;color:#374151;border-radius:5px;
                padding:1px 7px;font-size:10px;font-weight:500;">Level: {level}</span>
            <span style="background:#f3f4f6;color:#374151;border-radius:5px;
                padding:1px 7px;font-size:10px;">{for_students}</span>
            {cc_badge}
        </div>
        <div style="color:#6b7280;font-size:11px;margin-top:8px;padding-top:8px;
            border-top:1px solid #f3f4f6;line-height:1.5;">
            {explanation_short}
        </div>
    </div>
    """

def format_profile(profile: dict) -> str:
    if not profile:
        return """<div style="color:#9ca3af;font-size:13px;font-style:italic;
            text-align:center;padding:16px 0;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
            Start chatting to build your profile!</div>"""

    def section(title, content):
        return f"""<div style="margin-bottom:14px;">
            <div style="color:#6b7280;font-size:10px;font-weight:600;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                {title}</div>
            {content}</div>"""

    def tags(items, bg, color):
        if not items:
            return "<span style='color:#d1d5db;font-size:12px;'>None yet</span>"
        return " ".join(
            f"""<span style="background:{bg};color:{color};border-radius:6px;
                padding:2px 8px;font-size:11px;margin:2px;display:inline-block;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                {i}</span>""" for i in items
        )

    lang_levels = profile.get("language_levels", {})
    langs = [f"{l} - {v}" for l, v in lang_levels.items()]
    saved = profile.get("saved_channels_id", [])
    saved_html = (
        f"<span style='color:#7c3aed;font-size:12px;'>"
        f"{len(saved)} channel{'s' if len(saved) != 1 else ''} saved</span>"
        if saved else "<span style='color:#d1d5db;font-size:12px;'>None yet</span>"
    )
    channel_ratings = profile.get("channel_ratings", {})
    ratings_html = (
        "".join(
            f"""<div style="display:flex;justify-content:space-between;
                font-size:11px;padding:2px 0;color:#374151;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                <span>{ch[:20]}</span>
                <span style="color:#d97706;">{"⭐" * int(r)}</span></div>"""
            for ch, r in channel_ratings.items()
        )
        if channel_ratings
        else "<span style='color:#d1d5db;font-size:12px;'>None yet</span>"
    )

    return f"""<div style="padding:2px 0;">
        {section("Interests", tags(profile.get("interests", []), "#f0fdf4", "#15803d"))}
        {section("Dislikes", tags(profile.get("dislikes", []), "#fff1f2", "#be123c"))}
        {section("Languages", tags(langs, "#eff6ff", "#1d4ed8"))}
        {section("Saved Channels", saved_html)}
        {section("Channel Ratings", ratings_html)}
    </div>"""

# ── App State ─────────────────────────────────────────────────────────────────

_graph = None
_store = None
_thread_id = str(uuid.uuid4())
USER_ID = "default_user"

def get_graph():
    global _graph, _store
    if _graph is None:
        from graph import build_graph
        _graph, _store = build_graph()
    return _graph, _store

# ── Core Chat Function ────────────────────────────────────────────────────────

def chat(message: str) -> tuple[str, str, str]:
    graph, store = get_graph()

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config={
            "configurable": {
                "thread_id": _thread_id,
                "user_id": USER_ID
            },
            "recursion_limit": 50
        }
    )

    response_text = str(result["messages"][-1].content)

    cards_html = ""
    videos = result.get("videos")
    if videos:
        cards = "".join(
            format_video_card(v.model_dump() if hasattr(v, "model_dump") else v)
            for v in videos
        )
        cards_html = f"""
        <div style="padding:4px 0;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                {len(videos)} video{'s' if len(videos) != 1 else ''} found
            </div>
            {cards}
        </div>"""

    namespace = ("profile", USER_ID)
    memories = store.search(namespace)
    profile_data = memories[0].value if memories else {}

    return response_text, cards_html, format_profile(profile_data)

def clear_conversation():
    global _thread_id
    _thread_id = str(uuid.uuid4())
    return [], "", format_profile({}), ""

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: #f9fafb !important;
}
footer { display: none !important; }
.send-btn {
    background: #d97706 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    height: 46px !important;
    transition: background 0.15s !important;
}
.send-btn:hover { background: #b45309 !important; }
.clear-btn {
    background: transparent !important;
    color: #9ca3af !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}
.clear-btn:hover { color: #6b7280 !important; }
.input-box textarea {
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    background: white !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.input-box textarea:focus {
    border-color: #d97706 !important;
    box-shadow: 0 0 0 3px rgba(217,119,6,0.1) !important;
}
"""

# ── UI Layout ─────────────────────────────────────────────────────────────────

def build_ui():
    with gr.Blocks(title="Language Learning Agent") as demo:

        gr.HTML("""
        <div style="padding:24px 0 20px;border-bottom:1px solid #e5e7eb;margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:38px;height:38px;background:#d97706;border-radius:9px;
                    display:flex;align-items:center;justify-content:center;font-size:20px;">🌍</div>
                <div>
                    <div style="font-size:18px;font-weight:700;color:#111827;letter-spacing:-0.3px;
                        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                        Language Learning Agent</div>
                    <div style="color:#9ca3af;font-size:13px;
                        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                        Find YouTube videos that match your level and interests</div>
                </div>
            </div>
        </div>
        """)

        with gr.Row(equal_height=False):

            # ── Left: Chat ────────────────────────────────────────────────────
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    value=[],
                    height=480,
                    show_label=False,
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask me to find videos, analyze a video, or tell me your preferences...",
                        show_label=False,
                        lines=1,
                        scale=5,
                        elem_classes=["input-box"]
                    )
                    send_btn = gr.Button("Send →", scale=1, elem_classes=["send-btn"])

                with gr.Row():
                    clear_btn = gr.Button(
                        "🗑 Clear conversation",
                        elem_classes=["clear-btn"],
                        size="sm"
                    )

                gr.Examples(
                    examples=[
                        "Find me 5 French cooking videos at B1 level",
                        "I'm learning German at A2 and I love history",
                        "Find me Spanish tech videos at B2",
                        "I don't like politics content",
                        "Analyze this video: https://www.youtube.com/watch?v=kJQP7kiw5Fk",
                    ],
                    inputs=msg_input,
                    label="Try an example"
                )

            # ── Right: Sidebar ────────────────────────────────────────────────
            with gr.Column(scale=1, min_width=280):

                with gr.Accordion("👤 Your Profile", open=False):
                    profile_display = gr.HTML(value=format_profile({}))

                with gr.Accordion("🎬 Video Results", open=False):
                    video_cards = gr.HTML(
                        value="""<div style="color:#9ca3af;font-size:13px;
                            font-style:italic;text-align:center;padding:20px 0;
                            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                            No results yet. Ask me to find some videos!</div>"""
                    )

                gr.HTML("""
                <div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:12px;
                    padding:14px;margin-top:10px;
                    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                    <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:8px;">
                        How to use</div>
                    <div style="color:#6b7280;font-size:12px;line-height:1.8;">
                        💬 Ask for videos in any language<br>
                        🎯 Share your level for better results<br>
                        🔗 Paste a YouTube URL to analyze it<br>
                        ✏️ Tell me your interests and dislikes<br>
                        💾 Your profile is saved automatically
                    </div>
                </div>
                """)

        # ── Event Handlers ────────────────────────────────────────────────────

        def show_user_message(message: str, history: list):
            if not message.strip():
                return history, gr.update(), gr.update(), ""
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "⏳ Thinking..."}
            ]
            return history, gr.update(), gr.update(), ""

        def process_message(history: list):
            if not history or len(history) < 2:
                return history, "", format_profile({})
            message = history[-2]["content"]
            history = history[:-1]
            response_text, cards_html, profile_html = chat(message)
            history = history + [{"role": "assistant", "content": response_text}]
            return history, cards_html, profile_html

        send_btn.click(
            fn=show_user_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, video_cards, profile_display, msg_input]
        ).then(
            fn=process_message,
            inputs=[chatbot],
            outputs=[chatbot, video_cards, profile_display]
        )

        msg_input.submit(
            fn=show_user_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, video_cards, profile_display, msg_input]
        ).then(
            fn=process_message,
            inputs=[chatbot],
            outputs=[chatbot, video_cards, profile_display]
        )

        clear_btn.click(
            fn=clear_conversation,
            outputs=[chatbot, video_cards, profile_display]
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.amber,
            neutral_hue=gr.themes.colors.gray,
            font=gr.themes.GoogleFont("Inter"),
        )
    )
