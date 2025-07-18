import React, { useEffect, useRef } from "react";

interface ReparseNotifyProps {
  type: "success" | "error";
  message: string;
  duration?: number; // ms, undefined = persistent
  details?: string[]; // for bulk errors
  onClose?: () => void;
}

const colors = {
  success: "bg-green-600 text-white",
  error: "bg-red-600 text-white",
};

const ReparseNotify: React.FC<ReparseNotifyProps> = ({
  type,
  message,
  duration,
  details,
  onClose,
}) => {
  const detailsRef = useRef<HTMLDetailsElement>(null);

  // Auto-dismiss for success, persistent for error unless duration is set
  useEffect(() => {
    if (!onClose || type === "error" || !duration) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration, type]);

  // Copy error(s) to clipboard
  const handleCopy = () => {
    if (details && details.length > 0) {
      navigator.clipboard.writeText(details.join("\n"));
    } else {
      navigator.clipboard.writeText(message);
    }
  };

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm w-full px-4 py-3 rounded shadow-lg flex flex-col gap-2 ${colors[type]}`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold">{message}</span>
        {onClose && (
          <button
            className="ml-2 text-lg font-bold focus:outline-none"
            onClick={onClose}
            aria-label="Close notification"
          >
            ×
          </button>
        )}
      </div>
      {type === "error" && (
        <button
          className="text-xs underline font-semibold self-end"
          onClick={handleCopy}
          aria-label="Copy error message"
        >
          Copy {details && details.length > 0 ? "All Errors" : "Error"}
        </button>
      )}
      {details && details.length > 0 && (
        <details ref={detailsRef} className="bg-white bg-opacity-10 rounded p-2 mt-1">
          <summary className="cursor-pointer font-semibold underline">
            Show {details.length} error{details.length > 1 ? "s" : ""}
          </summary>
          <ul className="text-xs mt-2 max-h-40 overflow-y-auto">
            {details.map((d, i) => (
              <li key={i} className="mb-1 break-words">{d}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
};

export default ReparseNotify;