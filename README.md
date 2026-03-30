# AURA Analytics — Streamlit App


## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"

# 4. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Features

- **Dashboard** — stat cards, sentiment chart, recent articles, tracked companies
- **News Feed** — analyze any headline with VADER + TextBlob + LM + FinBERT
- **Companies** — add/remove companies, auto-syncs sentiment scores
- **Sentiment** — pie chart, radar model comparison, bar chart
- **Market** — correlation analysis, dual-axis chart, scatter plot

## Data

All data is stored locally in `data/` as JSON files:
- `data/articles.json` — analyzed news articles
- `data/companies.json` — tracked companies
- `data/snapshots.json` — market snapshots for correlation

