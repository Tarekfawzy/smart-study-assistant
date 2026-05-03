import streamlit as st
import requests
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Smart Study Assistant", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem; }
    .subtitle { text-align: center; color: #555; font-size: 1rem; margin-bottom: 1.5rem; }
    .answer-box { background: linear-gradient(135deg, #f8f9ff, #eef1ff); padding: 18px; border-radius: 14px; border-left: 5px solid #4f46e5; color: #1a1a2e; font-size: 0.95rem; line-height: 1.7; min-height: 200px; box-shadow: 0 2px 8px rgba(79,70,229,0.07); }
    .winner-badge { display: inline-block; background: #fbbf24; color: #1a1a2e; font-weight: 700; padding: 6px 18px; border-radius: 20px; font-size: 1rem; }
    .metric-card { background: #f8f9ff; border-radius: 12px; padding: 14px; text-align: center; border: 1px solid #e0e4ff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 Smart Study Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a file and ask questions — compare responses from multiple models</div>', unsafe_allow_html=True)
st.divider()

# Sidebar
st.sidebar.title("⚙️ Settings")
PRIVATEGPT_URL = st.sidebar.text_input("🌐 PrivateGPT URL", value="http://localhost:8001")

AVAILABLE_MODELS = ["llama3", "qwen3:8b", "mistral", "deepseek-r1:14b"]

compare_models = st.sidebar.multiselect(
    "Comparison Models:",
    AVAILABLE_MODELS,
    default=["llama3", "qwen3:8b"]
)

selected_model = st.sidebar.selectbox("Model for single questions", AVAILABLE_MODELS)

# File upload
st.subheader("📁 Upload File")
uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("Uploading file to PrivateGPT..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            resp = requests.post(f"{PRIVATEGPT_URL}/v1/ingest/file", files=files, timeout=120)
            if resp.status_code == 200:
                st.success("✅ File uploaded successfully!")
            else:
                st.error(f"❌ Upload failed: {resp.status_code}")
        except Exception as e:
            st.error(f"❌ Could not connect to PrivateGPT: {e}")

st.divider()

# Tabs
tab1, tab2 = st.tabs(["🔍 Compare Models", "💬 Single Question"])

COLORS = {
    "llama3": "#4f46e5",
    "qwen3:8b": "#10b981",
    "mistral": "#f59e0b",
    "deepseek-r1:14b": "#ef4444"
}

def get_color(model):
    for k, v in COLORS.items():
        if k in model:
            return v
    return "#6b7280"

def get_prompt(model, question):
    if "llama3" in model:
        return f"Explain in a simple and clear way for a beginner student.\nUse short sentences.\n\nQuestion:\n{question}"
    elif "qwen" in model:
        return f"Provide a precise, technical, and in-depth explanation.\nFocus on reasoning and concepts.\n\nQuestion:\n{question}"
    elif "mistral" in model:
        return f"Provide a detailed and well-structured explanation with examples.\nExplain step by step using bullet points.\n\nQuestion:\n{question}"
    elif "deepseek" in model:
        return f"Analyze the question and provide a logical, well-organized answer.\nThink step by step.\n\nQuestion:\n{question}"
    return question

with tab1:
    st.subheader("🔍 Compare Models")
    question_compare = st.text_area("✏️ Write your question here:", height=100, key="compare_q")
    use_context = st.checkbox("📚 Use context from uploaded file", value=True)

    if st.button("🚀 Start Comparison", disabled=not question_compare or len(compare_models) < 2):
        scores = {}
        results = {}
        times = {}
        word_counts = {}

        cols = st.columns(len(compare_models))
        placeholders = [cols[i].empty() for i in range(len(compare_models))]

        for i, model in enumerate(compare_models):
            placeholders[i].markdown(f"**🤖 {model}**\n\n⏳ Waiting...")

        for i, model in enumerate(compare_models):
            prompt = get_prompt(model, question_compare)
            placeholders[i].markdown(f"**🤖 {model}**\n\n🔄 Generating...")
            start = time.time()
            try:
                resp = requests.post(
                    f"{PRIVATEGPT_URL}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "model": model,
                        "use_context": use_context
                    },
                    timeout=600
                )
                elapsed = time.time() - start
                times[model] = round(elapsed, 2)

                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"]
                    results[model] = answer
                    word_counts[model] = len(answer.split())

                    score = 0
                    score += min(len(answer) * 0.08, 80)
                    if any(c in answer for c in ["-", "•", "*", "1.", "2."]):
                        score += 40
                    if any(w in answer.lower() for w in ["example", "for example", "such as"]):
                        score += 30
                    score += max(0, 40 - (elapsed * 5))
                    scores[model] = round(score, 1)

                    with cols[i]:
                        placeholders[i].empty()
                        st.markdown(f"**🤖 {model}** ✅")
                        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
                        st.caption(f"⏱️ {elapsed} sec | 📝 {word_counts[model]} words")
                else:
                    with cols[i]:
                        placeholders[i].error(f"❌ Error: {resp.status_code}")
            except Exception as e:
                with cols[i]:
                    placeholders[i].error(f"❌ {str(e)}")

        if scores:
            winner = max(scores, key=scores.get)
            st.markdown(f"""
            <div style="text-align:center; margin: 20px 0; padding: 16px; background: #f0fdf4; border-radius: 14px; border: 2px solid #22c55e;">
                🏆 <strong>Winner:</strong> <span class="winner-badge">{winner}</span> with score <strong>{scores[winner]}</strong>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📊 Performance Analytics")
            chart_col1, chart_col2 = st.columns(2)
            model_names = list(scores.keys())
            colors = [get_color(m) for m in model_names]

            with chart_col1:
                fig_score = go.Figure(go.Bar(
                    x=model_names,
                    y=[scores[m] for m in model_names],
                    marker_color=colors,
                    text=[f"{scores[m]}" for m in model_names],
                    textposition="outside",
                ))
                fig_score.update_layout(title="🏆 Score", height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_score, use_container_width=True)

            with chart_col2:
                fig_time = go.Figure(go.Bar(
                    x=model_names,
                    y=[times.get(m, 0) for m in model_names],
                    marker_color=colors,
                    text=[f"{times.get(m, '-')}s" for m in model_names],
                    textposition="outside",
                ))
                fig_time.update_layout(title="⏱️ Response Time (seconds)", height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_time, use_container_width=True)

with tab2:
    st.subheader("💬 Ask a Single Model")
    question_single = st.text_area("✏️ Write your question:", height=100, key="single_q")
    use_ctx_single = st.checkbox("📚 Use context from uploaded file", value=True, key="ctx_single")

    if st.button("🤖 Ask", disabled=not question_single):
        with st.spinner(f"Generating with {selected_model}..."):
            try:
                start = time.time()
                resp = requests.post(
                    f"{PRIVATEGPT_URL}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": question_single}],
                        "model": selected_model,
                        "use_context": use_ctx_single
                    },
                    timeout=300
                )
                elapsed = time.time() - start
                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"]
                    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
                    st.caption(f"⏱️ {round(elapsed, 2)} sec | 📝 {len(answer.split())} words")
                else:
                    st.error(f"❌ Error: {resp.status_code}")
            except Exception as e:
                st.error(f"❌ Could not connect to PrivateGPT: {e}")
