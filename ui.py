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
        padding:16px;margin:8px 0;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
            <a href="{url}" target="_blank"
                style="color:#111827;font-size:14px;font-weight:600;
                text-decoration:none;line-height:1.4;flex:1;"
                onmouseover="this.style.color='#d97706'"
                onmouseout="this.style.color='#111827'">
                {title}
            </a>
            <span style="background:{score_bg};color:{score_color};
                border:1px solid {score_border};border-radius:20px;
                padding:2px 10px;font-size:12px;font-weight:700;white-space:nowrap;">
                {score}/100
            </span>
        </div>
        <div style="color:#6b7280;font-size:12px;margin-top:5px;">
            {channel} &middot; {views_str} views
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;">
            <span style="background:#f3f4f6;color:#374151;border-radius:5px;
                padding:2px 8px;font-size:11px;font-weight:500;">Level: {level}</span>
            <span style="background:#f3f4f6;color:#374151;border-radius:5px;
                padding:2px 8px;font-size:11px;">{for_students}</span>
            {cc_badge}
        </div>
        <div style="color:#6b7280;font-size:12px;margin-top:10px;padding-top:10px;
            border-top:1px solid #f3f4f6;line-height:1.5;">
            {explanation_short}
        </div>
    </div>
    """

def format_news_card(article: dict) -> str:
    title = sanitize_text(article.get("title", "Unknown"))
    author = sanitize_text(article.get("author", "") or "")
    description = sanitize_text(article.get("description", "") or "")
    source = sanitize_text(article.get("source", ""))
    published_at = article.get("published_at", "")
    url = article.get("url", "#")
    date_str = published_at[:10] if published_at else ""
    description_short = description[:200] + ('...' if len(description) > 200 else '')
    author_html = (
        f'<span style="color:#9ca3af;font-size:11px;">By {author}</span>'
        if author else ""
    )

    return f"""
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;
        padding:16px;margin:8px 0;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:center;
            margin-bottom:8px;">
            <span style="background:#f3f4f6;color:#6b7280;border-radius:5px;
                padding:2px 8px;font-size:11px;font-weight:600;">
                {source}
            </span>
            <span style="color:#9ca3af;font-size:11px;">{date_str}</span>
        </div>
        <a href="{url}" target="_blank"
            style="color:#111827;font-size:14px;font-weight:600;
            text-decoration:none;line-height:1.4;display:block;margin-bottom:8px;"
            onmouseover="this.style.color='#d97706'"
            onmouseout="this.style.color='#111827'">
            {title}
        </a>
        <div style="color:#6b7280;font-size:12px;line-height:1.5;margin-bottom:8px;">
            {description_short}
        </div>
        {author_html}
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
                font-size:11px;padding:2px 0;color:#374151;">
                <span>{ch[:20]}</span>
                <span style="color:#d97706;">{"⭐" * int(r)}</span></div>"""
            for ch, r in channel_ratings.items()
        )
        if channel_ratings
        else "<span style='color:#d1d5db;font-size:12px;'>None yet</span>"
    )

    return f"""<div style="padding:2px 0;">
        {section("Video Interests", tags(profile.get("video_interests", []), "#f0fdf4", "#15803d"))}
        {section("Video Dislikes", tags(profile.get("video_dislikes", []), "#fff1f2", "#be123c"))}
        {section("News Interests", tags(profile.get("news_interests", []), "#f0fdf4", "#15803d"))}
        {section("News Dislikes", tags(profile.get("news_dislikes", []), "#fff1f2", "#be123c"))}
        {section("Languages", tags(langs, "#eff6ff", "#1d4ed8"))}
        {section("Preferred News Sources", tags(profile.get("prefered_news_sources", []), "#fdf4ff", "#7c3aed"))}
        {section("Saved Channels", saved_html)}
        {section("Channel Ratings", ratings_html)}
    </div>"""

def build_video_html(videos) -> str:
    cards = "".join(
        format_video_card(v.model_dump() if hasattr(v, "model_dump") else v)
        for v in videos
    )
    return f"""<div style="padding:4px 0;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;
            text-transform:uppercase;letter-spacing:0.8px;margin-bottom:12px;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
            {len(videos)} video{'s' if len(videos) != 1 else ''} found
        </div>{cards}</div>"""

def build_news_html(news) -> str:
    cards = "".join(
        format_news_card(a.model_dump() if hasattr(a, "model_dump") else a)
        for a in news
    )
    return f"""<div style="padding:4px 0;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;
            text-transform:uppercase;letter-spacing:0.8px;margin-bottom:12px;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
            {len(news)} article{'s' if len(news) != 1 else ''} found
        </div>{cards}</div>"""

EMPTY_VIDEOS = """<div style="color:#9ca3af;font-size:13px;font-style:italic;
    text-align:center;padding:40px 0;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    No video results yet. Ask me to find some videos!</div>"""

EMPTY_NEWS = """<div style="color:#9ca3af;font-size:13px;font-style:italic;
    text-align:center;padding:40px 0;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    No news results yet. Ask me to find some news!</div>"""

NODE_STATUS = {
    "orchestrator": "🧠 Understanding your request...",
    "youtube_search": "🎬 Searching YouTube and analyzing videos...",
    "transcript_only_pipeline": "📝 Analyzing video transcript...",
    "news_search_agent": "📰 Searching for news articles...",
    "profile_update_agent": "💾 Updating your profile...",
}

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

# ── Core Chat Function (generator) ───────────────────────────────────────────

def chat(message: str):
    """
    Generator that yields progress updates as the graph runs.
    Intermediate yields: (status_text, videos_or_None, news_or_None)
    Final yield:        (final_text, videos_or_None, news_or_None, profile_html)
    """
    graph, store = get_graph()

    final_videos = None
    final_news = None
    final_text = ""
    last_orchestrator_text = ""

    for chunk in graph.stream(
        {"messages": [HumanMessage(content=message)]},
        config={
            "configurable": {
                "thread_id": _thread_id,
                "user_id": USER_ID
            },
            "recursion_limit": 50
        }
    ):
        node_name = list(chunk.keys())[0]
        node_output = chunk[node_name]

        # Collect results as they arrive
        if isinstance(node_output, dict):
            if node_output.get("videos"):
                final_videos = node_output["videos"]
            if node_output.get("news"):
                final_news = node_output["news"]

            # Track orchestrator's latest text response
            if node_name == "orchestrator":
                msgs = node_output.get("messages", [])
                if msgs:
                    last_msg = msgs[-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        content = str(last_msg.content)
                        if content:
                            last_orchestrator_text = content

        status = NODE_STATUS.get(node_name, f"⚙️ Processing {node_name}...")
        yield status, final_videos, final_news

    # Final text is the last non-empty orchestrator response
    final_text = last_orchestrator_text

    # Read updated profile
    namespace = ("profile", USER_ID)
    memories = store.search(namespace)
    profile_data = memories[0].value if memories else {}

    yield final_text, final_videos, final_news, format_profile(profile_data)

def clear_conversation():
    global _thread_id
    _thread_id = str(uuid.uuid4())
    return [], EMPTY_VIDEOS, EMPTY_NEWS, format_profile({})

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
.gradio-container {
    max-width: 1200px !important;
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
    min-height: 46px !important;  /* match button height */
    padding-top: 12px !important;
    padding-bottom: 12px !important;
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

.results-tabs .tab-nav button {
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    border-radius: 8px 8px 0 0 !important;
}
.results-tabs .tab-nav button.selected {
    color: #d97706 !important;
    border-bottom: 2px solid #d97706 !important;
}


"""

# ── UI Layout ─────────────────────────────────────────────────────────────────

def build_ui():
    _, store = get_graph()
    namespace = ("profile", USER_ID)
    memories = store.search(namespace)
    profile_data = memories[0].value if memories else {}
    initial_profile_html = format_profile(profile_data)

    with gr.Blocks(title="Language Learning Agent") as demo:

        # Header
        gr.HTML("""
        <div style="padding:24px 0 20px;border-bottom:1px solid #e5e7eb;margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:50px;height:50px;
                    display:flex;align-items:center;justify-content:center;font-size:40px;">🌍</div>
                <div>
                    <div style="font-size:26px;font-weight:700;color:#111827;letter-spacing:-0.3px;
                        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                        Language Learning Agent</div>
                    <div style="color:#9ca3af;font-size:13px;
                        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                        Find YouTube videos and news that match your level and interests</div>
                </div>
            </div>
        </div>
        """)

        with gr.Row(equal_height=False):

            # ── Left: Chat + Results ──────────────────────────────────────────
            with gr.Column(scale=3):

                chatbot = gr.Chatbot(
                    value=[],
                    height=700,
                    show_label=False,
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask me to find videos, news, analyze a video, or tell me your preferences...",
                        show_label=False,
                        lines=1,
                        scale=5,
                        container=False,
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
                        "What are some interesting news in French today?",
                        "I'm learning German at A2 and I love history",
                        "Find me news about technology in Spanish",
                        "I don't like politics content",
                    ],
                    inputs=msg_input,
                    label="Try an example"
                )

                # Results tabs
                gr.HTML("""
                <div style="margin-top:20px;margin-bottom:8px;
                    font-size:12px;font-weight:600;color:#374151;
                    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                    Results
                </div>
                """)

                with gr.Tabs(elem_classes=["results-tabs"]):
                    with gr.Tab("🎬 Videos"):
                        video_cards = gr.HTML(value=EMPTY_VIDEOS)
                    with gr.Tab("📰 News"):
                        news_cards = gr.HTML(value=EMPTY_NEWS)

            # ── Right: Profile + How to use ───────────────────────────────────
            with gr.Column(scale=1, min_width=240):

                with gr.Accordion("👤 Your Profile", open=True):
                    profile_display = gr.HTML(value=initial_profile_html)

                gr.HTML("""
                <div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:12px;
                    padding:14px;margin-top:10px;
                    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                    <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:8px;">
                        How to use</div>
                    <div style="color:#6b7280;font-size:12px;line-height:1.8;">
                        💬 Ask for videos or news in any language<br>
                        🎯 Share your level for better results<br>
                        🔗 Paste a YouTube URL to analyze it<br>
                        ✏️ Tell me your interests and dislikes<br>
                        💾 Your profile is saved automatically
                    </div>
                </div>
                """)

        # ── Event Handlers ────────────────────────────────────────────────────

        def submit(message: str, history: list):
            """Show user message immediately and clear input."""
            if not message.strip():
                return history, gr.update(), gr.update(), gr.update(), ""
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "⏳ Starting..."}
            ]
            return history, gr.update(), gr.update(), gr.update(), ""

        def process_message(history: list):
            """Stream graph progress and yield updates."""
            if not history or len(history) < 2:
                return

            message = history[-2]["content"]
            base_history = history[:-1]  # remove placeholder

            video_html = EMPTY_VIDEOS
            news_html = EMPTY_NEWS
            profile_html = format_profile({})

            for result in chat(message):
                if len(result) == 3:
                    # Intermediate status update
                    status, videos, news = result
                    current_history = base_history + [
                        {"role": "assistant", "content": status}
                    ]
                    if videos:
                        video_html = build_video_html(videos)
                    if news:
                        news_html = build_news_html(news)
                    yield current_history, video_html, news_html, profile_html

                else:
                    # Final result
                    final_text, videos, news, profile_html = result
                    final_history = base_history + [
                        {"role": "assistant", "content": final_text}
                    ]
                    if videos:
                        video_html = build_video_html(videos)
                    if news:
                        news_html = build_news_html(news)
                    yield final_history, video_html, news_html, profile_html

        send_btn.click(
            fn=submit,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, video_cards, news_cards, profile_display, msg_input]
        ).then(
            fn=process_message,
            inputs=[chatbot],
            outputs=[chatbot, video_cards, news_cards, profile_display]
        )

        msg_input.submit(
            fn=submit,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, video_cards, news_cards, profile_display, msg_input]
        ).then(
            fn=process_message,
            inputs=[chatbot],
            outputs=[chatbot, video_cards, news_cards, profile_display]
        )

        clear_btn.click(
            fn=clear_conversation,
            outputs=[chatbot, video_cards, news_cards, profile_display]
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
