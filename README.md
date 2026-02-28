# 📚 Citation Source Analytics

An interactive Streamlit dashboard for visualizing academic citation source distributions.

## Features

- 🏛 **Institutions** — Bar chart, country pie chart, and treemap with country filter
- 🏷 **Topics** — Ranking chart, distribution pie, and bubble chart
- 📄 **Publication Types** — Donut chart, horizontal bar, and Pareto/cumulative chart

## Data Format

Place your data files in the `data/` folder:

| File | Columns |
|------|---------|
| `institution.txt` | `name\tcount\tcountry` |
| `topic.txt` | `name\tcount` |
| `type.txt` | `name\tcount` |

All files are **tab-separated** with a header row.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set **Main file path** to `app.py`
4. Click **Deploy**
