
import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState([]);
  const [selected, setSelected] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function searchMovies(event) {
    event.preventDefault();
    setError("");
    setMovies([]);
    setRecommendations([]);
    setSelected("");

    if (!query.trim()) return;

    try {
      const response = await fetch(
        `${API}/api/movies?q=${encodeURIComponent(query.trim())}`
      );

      if (!response.ok) {
        throw new Error(`Search failed: HTTP ${response.status}`);
      }

      const data = await response.json();
      setMovies(data.results || []);

      if (!data.results?.length) {
        setError("No movies found. Try another title.");
      }
    } catch (err) {
      setError(`Search error: ${err.message}`);
    }
  }

  async function getRecommendations(title) {
    setSelected(title);
    setRecommendations([]);
    setLoading(true);
    setError("");

    try {
      const url =
        `${API}/api/recommendations?title=${encodeURIComponent(title)}&limit=8`;

      const response = await fetch(url);

      if (!response.ok) {
        const data = await response.json();
        throw new Error(
          data.detail || `HTTP ${response.status}`
        );
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);

      if (!data.recommendations?.length) {
        setError("No recommendations were returned.");
      }
    } catch (err) {
      setError(`Recommendation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <h1>CineMatch</h1>
        <p>Discover your next favourite movie.</p>
      </header>

      <section className="search-section">
        <h2>Find a movie you love</h2>

        <form onSubmit={searchMovies} className="search-form">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search movies, e.g. 3 Idiots"
          />
          <button type="submit">Search</button>
        </form>

        {error && <p className="error">{error}</p>}

        {movies.length > 0 && (
          <div className="search-results">
            <h3>Search results — select a movie</h3>

            {movies.map((title, index) => (
              <button
                type="button"
                className="movie-option"
                key={`${title}-${index}`}
                onClick={() => getRecommendations(title)}
              >
                {title} — Get recommendations
              </button>
            ))}
          </div>
        )}
      </section>

      {selected && (
        <section>
          <h2>Movies similar to {selected}</h2>

          {loading && <p>Finding similar movies...</p>}

          {!loading && recommendations.length > 0 && (
            <section className="movie-grid">
              {recommendations.map((movie, index) => (
                <article
                  className="movie-card"
                  key={`${movie.tmdb_id || movie.title}-${index}`}
                >
                  {movie.poster_url ? (
                    <img
                      src={movie.poster_url}
                      alt={`${movie.title} poster`}
                      loading="lazy"
                    />
                  ) : (
                    <div className="poster-placeholder">
                      No poster available
                    </div>
                  )}

                  <div className="movie-info">
                    <h3>{movie.title}</h3>

                    {movie.release_date && (
                      <p>{movie.release_date.slice(0, 4)}</p>
                    )}

                    {movie.rating != null && (
                      <p>
                        ⭐ {Number(movie.rating).toFixed(1)} / 10
                      </p>
                    )}

                    <p className="overview">
                      {movie.overview || "No description available."}
                    </p>
                  </div>
                </article>
              ))}
            </section>
          )}
        </section>
      )}
    </main>
  );
}

export default App;
