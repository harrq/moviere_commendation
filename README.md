# 🎬 CineMatch — Movie Recommendation System

CineMatch is a movie recommendation web application that helps users discover movies similar to their favorites. It combines content-based filtering with a modern React interface and The Movie Database (TMDB) API to display movie details.

## ✨ Features

- 🔎 Search for movies by title
- 🎯 Get recommendations for similar movies
- 🖼️ View movie posters and ratings
- 📅 Explore release dates and movie overviews
- ⚡ FastAPI backend and responsive React frontend

## 🛠️ Tech Stack

**Frontend:** React, Vite, JavaScript, CSS  
**Backend:** Python, FastAPI  
**Machine Learning:** TF-IDF, cosine similarity  
**Movie Data:** TMDB API  
**Model Storage:** Pickle/joblib-compatible model artifacts

## 📁 Project Structure

```text
movie_recommend/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
├── model/
│   ├── df.pkl
│   ├── indices.pkl
│   ├── tf_idf.pkl
│   └── tfidf_matrix.pkl
├── movies.csv
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/harrq/moviere_commendation.git
cd moviere_commendation
```

### 2. Set up the Python backend

Create and activate a virtual environment, then install the backend dependencies.

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 3. Configure the TMDB API key

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key
```

Replace the placeholder with your own API key. Never commit your `.env` file.

### 4. Start the backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend: http://localhost:8000  
API documentation: http://localhost:8000/docs

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## 🔮 Future Improvements

- Deploy the frontend and backend online
- Add genre and release-year filters
- Improve recommendation quality and evaluation
- Add watchlists and user preferences
- Add automated tests and error handling

## ⚠️ Notes

You need a valid TMDB API key for API-dependent movie information. Recommendation quality depends on the available dataset and model.

This product uses the TMDB API but is not endorsed or certified by TMDB.

## 👨‍💻 Author

Developed as a movie recommendation project using Python, machine learning, and React.
