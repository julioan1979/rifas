# Run instructions (local / Streamlit Cloud / Codespaces)

Quick steps to run the app locally:

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure Supabase credentials

- Option A — Local `.env` (recommended for development):

  Copy `.env.template` to `.env` and fill the values:

  ```text
  SUPABASE_URL=https://your-project-ref.supabase.co
  SUPABASE_KEY=your_anon_or_service_key_here
  ```

  The app already uses `python-dotenv` and loads `.env` automatically.

- Option B — Environment variables (temporary shell session):

  ```bash
  export SUPABASE_URL='https://your-project-ref.supabase.co'
  export SUPABASE_KEY='your_anon_or_service_key_here'
  ```

- Option C — Streamlit Cloud / Streamlit deployment:

  In Streamlit Cloud, open your app, go to **App settings → Secrets**, and add:

  ```toml
  [supabase]
  url = "https://your-project-ref.supabase.co"
  key = "your_anon_or_service_key_here"
  ```

4. (Optional) Run the DB migration to add `preco_unitario` column

Copy the SQL in `scripts/add_preco_unitario_to_blocos_rifas.sql` to your Supabase SQL editor and run it. Make a backup if you want.

5. Run the app

```bash
streamlit run app.py --server.port 8501
```

6. Open in browser

```bash
$BROWSER http://localhost:8501
```

Troubleshooting
- If `streamlit: command not found` after installing, check `which streamlit` and ensure your virtualenv is activated.
- If you get `Credenciais do Supabase não encontradas`, verify `.env` exists or that environment variables are exported.
