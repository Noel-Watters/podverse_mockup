//Used to Add RSS Feeds on RSS Feed Page
import React, { useState } from "react";

interface AddRssFeedModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function AddRssFeedModal({ open, onClose, onSuccess }: AddRssFeedModalProps) {
  const [urls, setUrls] = useState<string[]>([""]);
  const [priorities, setPriorities] = useState<string[]>([""]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleUrlChange = (idx: number, value: string) => {
    setUrls(urls => urls.map((url, i) => (i === idx ? value : url)));
  };

  const handlePriorityChange = (idx: number, value: string) => {
    setPriorities(priorities => priorities.map((p, i) => (i === idx ? value : p)));
  };

  const handleAddField = () => {
    setUrls(urls => [...urls, ""]);
    setPriorities(priorities => [...priorities, ""]);
  };

  const handleRemoveField = (idx: number) => {
    if (urls.length > 1) {
      setUrls(urls => urls.filter((_, i) => i !== idx));
      setPriorities(priorities => priorities.filter((_, i) => i !== idx));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      for (let i = 0; i < urls.length; i++) {
        const url = urls[i].trim();
        if (!url) continue;
        const payload: any = { url };
        const priority = priorities[i].trim();
        if (priority !== "") {
          payload.parsing_priority = Number(priority);
        }
        const res = await fetch("/api/feeds", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || "Failed to add feed");
        }
      }
      setMessage("Success! Feed(s) added.");
      setLoading(false);
      setTimeout(() => {
        setMessage(null);
        onClose();
        onSuccess && onSuccess();
      }, 1500);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || "Failed to add feed(s)");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
        <button className="absolute top-2 right-2 text-gray-400 hover:text-black" onClick={onClose}>
          &times;
        </button>
        <h2 className="text-xl font-bold mb-4">Add RSS Feed(s)</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {urls.map((url, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <input
                type="text"
                value={url}
                onChange={e => handleUrlChange(idx, e.target.value)}
                placeholder="Feed URL"
                className="flex-1 border rounded px-3 py-2 text-gray-900"
              />
              <input
                type="number"
                min={0}
                max={5}
                value={priorities[idx]}
                onChange={e => handlePriorityChange(idx, e.target.value)}
                placeholder="Priority"
                className="w-20 border rounded px-2 py-2 text-gray-900"
              />
              {urls.length > 1 && (
                <button type="button" onClick={() => handleRemoveField(idx)} className="text-red-500 px-2">
                  Remove
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddField} className="text-blue-500 underline">
            + Add another
          </button>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded mt-2"
            disabled={loading}
          >
            {loading ? "Adding..." : "Add All"}
          </button>
          {message && <div className="text-green-600 text-center">{message}</div>}
          {error && <div className="text-red-600 text-center">{error}</div>}
        </form>
      </div>
    </div>
  );
}