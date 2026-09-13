import React from 'react';
import { useState } from 'react';

const BACKEND_URL = 'https://customer-sentiment-te99.onrender.com'; // Change if your backend runs elsewhere

const SentimentAnalyzer: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeSentiment = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await response.json();
      if (response.ok) {
        setResult(data.sentiment || JSON.stringify(data));
      } else {
        setError(data.error || 'Unknown error');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 p-6 rounded-lg shadow-lg max-w-md mx-auto mt-10 text-white">
      <h2 className="text-2xl font-bold mb-4 text-blue-400">Sentiment Analyzer</h2>
      <textarea
        className="w-full p-2 rounded bg-gray-800 border border-gray-700 text-white mb-4"
        rows={4}
        placeholder="Enter text to analyze..."
        value={text}
        onChange={e => setText(e.target.value)}
      />
      <button
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50"
        onClick={analyzeSentiment}
        disabled={loading || !text.trim()}
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      {result && (
        <div className="mt-4 p-3 rounded bg-gray-800 border border-blue-700">
          <span className="font-semibold text-blue-300">Sentiment:</span> {result}
        </div>
      )}
      {error && (
        <div className="mt-4 p-3 rounded bg-red-900 border border-red-700 text-red-300">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default SentimentAnalyzer;