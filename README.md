# Wing Lab 🍗

A chat-style wing recipe generator powered by Google Gemini AI — completely free.

## Setup in PyCharm

### 1. Install dependencies
Open the terminal in PyCharm and run:
```
pip install -r requirements.txt
```

### 2. Add your Gemini API key
Create this folder and file inside your project:
```
.streamlit/
    secrets.toml
```

Paste this into `secrets.toml` (use your real key):
```toml
GEMINI_API_KEY = "your-key-here"
```

### 3. Run locally
```
streamlit run app.py
```
Streamlit opens the app in your browser automatically.

---

## Deploy publicly on Streamlit Cloud

1. Push this folder to a **GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → connect your repo
3. Under **Advanced settings → Secrets**, paste:
   ```
   GEMINI_API_KEY = "your-key-here"
   ```
4. Hit Deploy → you get a free public URL like `https://yourapp.streamlit.app`

Your API key stays private on Streamlit's servers. Free for recreational use.
