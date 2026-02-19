# Urdu Children’s Story Generation System

A complete Urdu NLP pipeline and web application that generates children’s stories from a short user prompt.

The project combines classical language modeling with a practical product stack:

- Data collection and cleaning for Urdu story text
- Custom Byte Pair Encoding (BPE) tokenizer
- Trigram language model with interpolated smoothing
- FastAPI inference service
- Next.js frontend with right-to-left (RTL) Urdu UX

---

## What this project is about

This system is designed to demonstrate an end-to-end Urdu text generation workflow without large transformer infrastructure. It focuses on reproducibility, interpretability, and lightweight deployment.

Given a short Urdu prefix (for example: `ایک دن`), the model generates a continuation as a story and returns it through an API used by the frontend.

---

## Core objectives

- Build a clean Urdu corpus from story sources
- Preserve Urdu script quality during preprocessing and normalization
- Learn reusable subword units via BPE
- Train a statistical language model over tokenized text
- Expose generation through a simple, production-style API and UI

---

## System architecture

1. User enters Urdu prompt in frontend.
2. Frontend sends `POST /generate` request to backend.
3. Backend encodes prompt using learned BPE merges.
4. Trigram model samples next tokens using interpolation.
5. Token stream is decoded to formatted Urdu text.
6. Story is returned and rendered in RTL layout.

### Modeling strategy

The next-token probability uses linear interpolation:

$$
P(w_3|w_1,w_2)=\lambda_1P(w_3)+\lambda_2P(w_3|w_2)+\lambda_3P(w_3|w_1,w_2)
$$

Default weights in code are $(0.1, 0.3, 0.6)$, favoring trigram context while remaining robust to sparsity.

---

## Repository structure

```text
Urdu-Children-s-Story-Generation-System/
├── backend/
│   ├── api.py                    # FastAPI app and generation endpoint
│   ├── requirements.txt          # Backend dependencies
│   ├── Dockerfile                # Containerization for backend
│   └── DOCKER_README.md
├── data/
│   ├── scrape_stories_selenium.py  # Optional data scraping script
│   ├── preprocess_stories.py       # Cleaning + normalization + control tokens
│   └── processed/
│       └── corpus.txt              # Training corpus used by tokenizer/model
├── frontend/
│   ├── pages/index.js            # Main app page
│   ├── components/               # Input and output UI components
│   └── package.json
├── tokenizer/
│   ├── bpe_tokenizer.py          # Train/load/encode/decode BPE
│   ├── train_bpe.py              # Tokenizer training pipeline
│   ├── merges.txt                # Learned merge rules
│   └── vocab.json                # Learned vocabulary
├── model/
│   ├── trigram_model.py          # N-gram counting + generation
│   ├── train_trigram.py          # Model training script
│   └── trigram_model.pkl         # Serialized model artifact
├── utils/
│   └── constants.py              # Shared special tokens and helpers
└── raw/data/                     # Raw downloaded story files
```

---

## How each module works

### 1) `utils/` (shared constants)

`utils/constants.py` defines special control tokens in a Unicode private-use range:

- `EOS`: end of sentence
- `EOP`: end of paragraph
- `EOT`: end of story/text

These are intentionally selected to avoid collisions with natural Urdu text, and are used consistently across preprocessing, tokenization, training, and decoding.

### 2) `data/` (collection + preprocessing)

- `scrape_stories_selenium.py` collects story URLs and content.
- `preprocess_stories.py` normalizes Urdu characters, removes unwanted text/noise, preserves Urdu punctuation, and injects special tokens for structural boundaries.

### 3) `tokenizer/` (BPE)

- Initializes vocabulary at character level with end-of-word marker `</w>`.
- Iteratively merges the most frequent adjacent symbol pairs.
- Saves learned artifacts to `vocab.json` and `merges.txt`.
- Uses learned merges at inference time to encode user prompts.

### 4) `model/` (trigram LM)

- Counts unigrams, bigrams, and trigrams over BPE token stream.
- Applies interpolated smoothing for generation stability.
- Samples next tokens until `EOT` or maximum length.
- Decodes token stream back to readable Urdu story text.

### 5) `backend/` (serving)

- Loads tokenizer and model once at startup.
- Exposes generation endpoint via FastAPI.
- Returns JSON responses suitable for web integration.

### 6) `frontend/` (user interface)

- Next.js app with Urdu RTL input/output behavior.
- Sends user prefix to backend and renders generated story.
- Includes loading and basic error handling states.

---

## Quick start (inference only)

Use this path if trained artifacts already exist:

- `tokenizer/merges.txt`
- `tokenizer/vocab.json`
- `model/trigram_model.pkl`

### Backend

```bash
cd backend
pip install -r requirements.txt
python api.py
```

Backend URL: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:3000`

---

## API contract

### `GET /`

Health/status endpoint. Returns service and model metadata.

### `POST /generate`

Request:

```json
{
  "prefix": "ایک دن",
  "max_length": 500
}
```

Validation:

- `prefix`: required string
- `max_length`: integer from `10` to `2000` (default `500`)

Response:

```json
{
  "story": "...generated urdu story..."
}
```

Example request:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prefix":"ایک دن","max_length":50}'
```

---

## Rebuild pipeline (from raw text)

### Step 1: Optional scraping

```bash
pip install selenium webdriver-manager beautifulsoup4 requests
cd data
python scrape_stories_selenium.py
```

### Step 2: Preprocess corpus

```bash
cd data
python preprocess_stories.py
```

This script writes processed output and inserts structural control tokens.

> Important: tokenizer training reads `data/processed/corpus.txt`. Ensure your final processed corpus is available at that exact location before training.

### Step 3: Train BPE tokenizer

```bash
cd tokenizer
python train_bpe.py
```

### Step 4: Train trigram model

```bash
cd model
python train_trigram.py
```

### Step 5: Start backend and frontend

Run the quick start commands above.

---

## Docker (backend service)

From repository root:

```bash
docker build -f backend/Dockerfile -t urdu-story-api .
docker run -p 8000:8000 urdu-story-api
```

Available URLs:

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

---

## Operational notes

- The frontend currently calls backend at `http://localhost:8000` directly.
- Generation is stochastic; same prompt can produce different outputs.
- Quality depends strongly on corpus quality and domain coverage.
- This classical LM is lightweight and interpretable, but less fluent than modern large transformer models.

---

## Troubleshooting

### Frontend cannot generate stories

- Confirm backend is running on port `8000`.
- Check browser console/network for request failures.
- Verify CORS settings in backend for local frontend origin.

### Backend startup fails

- Ensure model/tokenizer artifacts exist and paths are correct.
- Start from expected directories (`backend`, `model`, `tokenizer`) when running scripts.

### Scraper errors

- Update Chrome and retry.
- Reinstall scraping dependencies.
- Ensure stable internet access.

### Urdu text rendering issues

- Keep all files in UTF-8.
- Use a browser/font stack with strong Urdu support.

---


