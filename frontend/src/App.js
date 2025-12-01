import { useState } from "react";
import "./index.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: query })
      });
      const data = await res.json();
      setResults(data.results);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-heading">Pokémon Dex Search</h1>

      <div className="search-container">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a query..."
          className="search-input"
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <button onClick={handleSearch} className="search-button">
          Search
        </button>
      </div>

      {loading && <p className="loading">Searching...</p>}

      <ul className="results-list">
        {results.map((r, i) => (
          <li key={i} className="result-item">
            <b>Pokémon ID {r.id}</b>: {r.text}
            <div className="result-distance">
              Distance: {r.distance.toFixed(3)}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
