# Urdu Story Generator Frontend

A Next.js frontend application for generating Urdu stories using AI.

## Getting Started

### 1. Start Backend
```bash
cd backend
python api.py
```
✅ Backend running on `http://localhost:8000`

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend running on `http://localhost:3000`

### 3. Open Application
Open [http://localhost:3000](http://localhost:3000) in your browser and start generating Urdu stories!

## Features

- Urdu text input with RTL (right-to-left) support
- Story generation using backend API
- Responsive design with Tailwind CSS
- Clean and minimal UI

## Backend API

Make sure the backend API is running on `http://localhost:8000` before using the application.

## Project Structure

```
frontend/
├── components/
│   ├── StoryInput.js    # Input component for story prefix
│   └── StoryOutput.js   # Output component for generated story
├── pages/
│   ├── _app.js          # Next.js app wrapper
│   ├── _document.js     # Custom document with RTL support
│   └── index.js         # Main page
├── styles/
│   └── globals.css      # Global styles with Tailwind
└── package.json
```
