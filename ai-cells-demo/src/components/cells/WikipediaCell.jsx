import React, { useState } from 'react';
import { Link2, Table, Loader2 } from 'lucide-react';

const WikipediaCell = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tables, setTables] = useState([]);

  const validateUrl = (url) => {
    if (!url || url.length < 10) { // Basic length check for complete URL
      return { valid: false, message: 'Please enter a complete Wikipedia URL' };
    }
    
    try {
      const urlObj = new URL(url);
      if (!urlObj.hostname.includes('wikipedia.org')) {
        return { valid: false, message: 'URL must be from wikipedia.org' };
      }
      return { valid: true };
    } catch {
      return { valid: false, message: 'Please enter a valid URL' };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validation = validateUrl(url);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/cells/wikipedia/extract/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin',
        body: JSON.stringify({ source: url }),
      });

      // Check if response exists
      if (!response) {
        throw new Error('No response received from server');
      }

      // Log response headers for debugging
      console.log('Response headers:', Object.fromEntries(response.headers));
      console.log('Response status:', response.status);

      let data;
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.error('Invalid content type:', contentType);
        setError('Invalid response format from server');
        return;
      }

      try {
        const text = await response.text();
        console.log('Raw response:', text);
        data = JSON.parse(text);
      } catch (err) {
        console.error('JSON parse error:', err);
        setError('Failed to parse server response');
        return;
      }

      if (!response.ok) {
        setError(data.message || 'Failed to extract tables');
        return;
      }

      if (!data.data?.tables) {
        setError('Invalid response format from server');
        return;
      }

      setTables(data.data.tables);
    } catch (err) {
      console.error('Request error:', err);
      setError('Failed to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-2 space-y-2">
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
              <Link2 className="h-4 w-4 text-muted-foreground" />
            </div>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter Wikipedia URL"
              className="w-full pl-9 pr-4 py-2 rounded-md border bg-background"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !url}
            className={`
              px-4 py-2 rounded-md font-medium
              ${loading ? 'bg-primary/50' : 'bg-primary hover:bg-primary/90'}
              text-primary-foreground disabled:cursor-not-allowed
            `}
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Table className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}

      {tables.length > 0 && (
        <div className="space-y-2">
          {tables.map((table, index) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <table className="w-full">
                {table.title && (
                  <caption className="px-2 py-1 bg-muted font-medium border-b text-left">
                    {table.title}
                  </caption>
                )}
                <thead>
                  <tr className="border-b bg-muted/50">
                    {table.headers.map((header, i) => (
                      <th key={i} className="px-2 py-1 text-left font-medium">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {table.data.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b last:border-0">
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex} className="px-2 py-1">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WikipediaCell;
