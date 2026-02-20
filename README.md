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
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions CI/CD pipeline
├── api/
│   └── generate.py               # Vercel serverless function for generation
├── components/
│   ├── StoryInput.js             # Input UI component
│   └── StoryOutput.js            # Output UI component
├── data/
│   ├── scrape_stories_selenium.py  # Optional data scraping script
│   ├── preprocess_stories.py       # Cleaning + normalization + control tokens
│   └── processed/
│       └── corpus.txt              # Training corpus used by tokenizer/model
├── model/
│   ├── trigram_model.py          # N-gram counting + generation
│   ├── train_trigram.py          # Model training script
│   └── trigram_model.pkl         # Serialized model artifact
├── pages/
│   ├── _app.js                   # Next.js app wrapper
│   ├── _document.js              # Custom document
│   └── index.js                  # Main page
├── styles/
│   └── globals.css               # Global styles
├── tests/
│   └── test_api_generate.py     # Backend API unit tests
├── tokenizer/
│   ├── bpe_tokenizer.py          # Train/load/encode/decode BPE
│   ├── train_bpe.py              # Tokenizer training pipeline
│   ├── merges.txt                # Learned merge rules
│   └── vocab.json                # Learned vocabulary
├── utils/
│   └── constants.py              # Shared special tokens and helpers
├── raw/data/                     # Raw downloaded story files
├── next.config.js                # Next.js configuration
├── package.json                  # Node dependencies
└── tailwind.config.js            # Tailwind CSS configuration
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

### 5) `api/` (serverless backend)

- Vercel serverless function handler for story generation.
- Loads tokenizer and model on cold start (cached on warm starts).
- Exposes generation endpoint at `/api/generate`.
- Returns JSON responses with generated stories.

### 6) `pages/` and `components/` (Next.js frontend)

- Next.js app with Urdu RTL input/output behavior.
- `pages/index.js` contains main application logic.
- `components/StoryInput.js` handles user input.
- `components/StoryOutput.js` renders generated stories.
- Includes loading states and error handling.

### 7) `tests/` (automated testing)

- `test_api_generate.py` contains backend API unit tests.
- Tests invalid JSON, empty prefix, and successful generation flows.
- Uses pytest with mocked dependencies for fast execution.

---

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and continuous deployment.

### Pipeline jobs

**1. Frontend Build (`frontend-build`)**
- Installs Node.js dependencies
- Builds Next.js production bundle
- Validates build passes without errors

**2. Python Validation (`python-validation`)**
- Compiles Python syntax across all modules
- Validates core imports (tokenizer, model, utils)
- Runs backend API unit tests with pytest

**3. Deploy to Vercel (`deploy-vercel`)**
- Runs only after CI jobs pass
- Deploys only on push to `main` branch
- Requires GitHub secrets for authentication
- Automatically updates production on Vercel

### Workflow triggers

- **Automatic:** push to `main`, `master`, or `develop` branches
- **Automatic:** pull requests to these branches
- **Manual:** workflow dispatch button in Actions tab

### Required GitHub Secrets

For automatic Vercel deployment, add these secrets in repository settings:

- `VERCEL_TOKEN`: Personal access token from Vercel account
- `VERCEL_ORG_ID`: Your Vercel organization/team ID
- `VERCEL_PROJECT_ID`: Target project ID

**How to obtain secrets:**

1. **VERCEL_TOKEN:**
   - Vercel Dashboard → Account Settings → Tokens → Create Token

2. **VERCEL_ORG_ID and VERCEL_PROJECT_ID:**
   - Run `npx vercel link` in project root
   - Open `.vercel/project.json`
   - Copy `orgId` and `projectId` values

3. **Add to GitHub:**
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret for each value

### Manual workflow run

To trigger CI/CD manually without pushing code:

1. Go to repository on GitHub → Actions tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Choose branch and click "Run workflow" button

---

## Deployment

### Vercel (Production)

This project is configured for Vercel serverless deployment.

**Automatic deployment:**
- Push to `main` branch triggers automatic deployment via GitHub Actions
- CI checks must pass before deployment starts

**Manual deployment:**
```bash
npm install -g vercel
vercel --prod
```

**Environment:**
- Frontend: Static Next.js pages
- Backend: Serverless function at `/api/generate`
- Python runtime: Managed by Vercel with `uv` package manager

---

## Quick start (local development)

Use this path if trained artifacts already exist:

- `tokenizer/merges.txt`
- `tokenizer/vocab.json`
- `model/trigram_model.pkl`

### Install dependencies

```bash
npm install
```

### Run development server

```bash
npm run dev
```

Application URL: `http://localhost:3000`

The serverless function will be available at `http://localhost:3000/api/generate`

---

## API contract

### `POST /api/generate`

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
  "story": "...generated urdu story...",
  "prefix": "ایک دن",
  "tokens_generated": 42
}
```

Error response:

```json
{
  "error": "Missing or empty 'prefix' field",
  "status": 400
}
```

Example request (local dev):

```bash
curl -X POST "http://localhost:3000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prefix":"ایک دن","max_length":50}'
```

Example request (production):

```bash
curl -X POST "https://your-app.vercel.app/api/generate" \
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

### Step 5: Start development server

Run the quick start commands above.

---

## Running tests

### Backend API tests

```bash
pip install pytest
python -m pytest tests/test_api_generate.py -v
```

### Run all tests (as in CI)

```bash
# Python syntax validation
python -m compileall api model tokenizer utils data

# Import checks
python -c "from tokenizer.bpe_tokenizer import load_tokenizer, encode"
python -c "from model.trigram_model import load_model, generate_story"
python -c "from utils.constants import EOS, EOP, EOT, SPECIAL_TOKENS"

# Backend unit tests
python -m pytest -q tests/test_api_generate.py
```

---

## Operational notes

- The frontend calls the serverless API at `/api/generate`.
- Generation is stochastic; same prompt can produce different outputs.
- Quality depends strongly on corpus quality and domain coverage.
- This classical LM is lightweight and interpretable, but less fluent than modern large transformer models.
- Model artifacts are loaded on serverless function cold start and cached across warm invocations.

---

## Troubleshooting

### Frontend cannot generate stories

- Confirm development server is running on port `3000`.
- Check browser console/network for request failures.
- Verify model artifacts exist in correct paths.
- Check serverless function logs in terminal or Vercel dashboard.

### Serverless function errors

- Ensure model/tokenizer artifacts exist and paths are correct.
- Verify Python imports resolve properly.
- Check that all special tokens are defined in `utils/constants.py`.
- Review function logs for detailed error messages.

### CI/CD pipeline failing

- **Frontend build fails:** Check `package.json` dependencies and Next.js configuration.
- **Python validation fails:** Verify syntax and imports in affected modules.
- **Backend tests fail:** Run `python -m pytest tests/` locally to debug.
- **Vercel deploy fails:** Ensure GitHub secrets are set correctly and `uv` is available.

### Vercel deployment issues

- Verify all three secrets are configured in GitHub repository settings.
- Check Vercel project is linked correctly with `npx vercel link`.
- Ensure Python runtime version matches CI configuration (3.11).
- Review Vercel deployment logs for detailed error messages.

### Scraper errors

- Update Chrome and retry.
- Reinstall scraping dependencies.
- Ensure stable internet access.

### Urdu text rendering issues

- Keep all files in UTF-8.
- Use a browser/font stack with strong Urdu support.

---


