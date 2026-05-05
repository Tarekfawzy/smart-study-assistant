# 🎓 Smart Study Assistant

> A local AI-powered study tool that helps you understand your lectures using multiple LLM models — privately, offline, and fast.

---

## 💡 What is this?

Ever missed a lecture or struggled to understand one? **Smart Study Assistant** lets you upload your lecture (PDF or TXT) and ask questions about it — powered by multiple local AI models running on your own machine.

No internet required. No data leaves your computer.

---

## ✨ Features

- 📄 **Upload your lecture** — supports PDF and TXT files
- 🤖 **4 AI Models available** — llama3, qwen3:8b, mistral, deepseek-r1
- 💬 **Single Question mode** — ask one model a focused question
- 🔍 **Compare Models mode** — ask all models the same question and compare their answers side by side
- 📊 **Model Comparison metrics** — see which model:
  - Answered the fastest ⚡
  - Gave the most accurate response ✅
  - Provided the right amount of detail 📝

---

## 🚀 How to Use

1. Make sure **PrivateGPT** and **Ollama** are running locally
2. Open the app in your browser at `http://localhost:8501`
3. Upload your lecture file (PDF or TXT)
4. Wait for the file to be sent to PrivateGPT
5. Type your question
6. Choose:
   - **Single Question** → pick one model and get a direct answer
   - **Compare Models** → ask all models and compare results

---

## 🛠️ Requirements

- [PrivateGPT](https://github.com/zylon-ai/private-gpt) running on `http://localhost:8001`
- [Ollama](https://ollama.com/) with the following models pulled:
  ```
  ollama pull llama3
  ollama pull qwen3:8b
  ollama pull mistral
  ollama pull deepseek-r1:14b
  ```
- Python 3.10+
- Streamlit

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
smart-study-assistant/
├── app.py              # Main Streamlit app
├── ocr_pdf.py          # OCR support for image-based PDFs
├── settings.yaml       # PrivateGPT configuration
└── README.md
```

---

## 👨‍💻 Built by

Built by: Smart Study Assistant Team
Faculty of Computers and Artificial Intelligence
Sphinx University, 2026
