import type { Message } from "../../types";
import { Copy, Check, Loader2, Download } from "lucide-react";
import { useState } from "react";
import type { TimelineStep } from "../../types";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState<number | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleCopy = () => {
    if (typeof message.content === "string") {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isUser = message.role === "user";

  // timeline rendering
  const renderTimeline = (steps: TimelineStep[]) => {
    return (
      <div className="space-y-2">
        {steps.map((step) => {
          let icon = null;
          let statusClass = "text-muted-foreground";
          if (step.status === "completed") {
            icon = <Check className="w-4 h-4 text-green-500" />;
            statusClass = "text-green-500";
          } else if (step.status === "processing") {
            icon = <Loader2 className="w-4 h-4 animate-spin text-primary" />;
            statusClass = "text-primary";
          } else if (step.status === "failed") {
            icon = (
              <svg
                className="w-4 h-4 text-red-500"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 9v4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <circle cx="12" cy="16" r="1" fill="currentColor" />
              </svg>
            );
            statusClass = "text-red-500";
          } else if (step.status === "queued") {
            icon = (
              <svg
                className="w-4 h-4 text-yellow-500"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 2v6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            );
            statusClass = "text-yellow-500";
          } else {
            // pending
            icon = <div className="w-4 h-4 rounded-full bg-gray-300" />;
          }

          return (
            <div key={step.key} className="flex items-start gap-3">
              <div className="mt-0.5">{icon}</div>
              <div>
                <div className={`text-sm font-medium ${statusClass}`}>
                  {step.title}
                </div>
                {step.detail && (
                  <div className="text-xs text-muted-foreground">
                    {step.detail}
                  </div>
                )}
                {step.timestamp && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {new Date(step.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // If message contains a download URL (e.g. "/api/download/<job_id>") return it, otherwise null
  const extractDownloadUrl = (
    text: string
  ): { url: string; jobId: string } | null => {
    // Accept full or relative URL: /api/download/..., https://host/api/download/...
    const regex = /(?:https?:\/\/[^\/]+)?(\/api\/download\/([a-f0-9\-]+))/i;
    const m = text.match(regex);
    if (m && m[1]) {
      // m[1] is the relative path, m[2] is jobId
      const relative = m[1];
      const jobId = m[2];
      // Use same-origin absolute URL so fetch('/api/download/..') works; we'll keep relative path
      return { url: relative, jobId };
    }
    return null;
  };

  const handleDownload = (downloadUrl: string, jobId: string) => {
    const base = import.meta.env.VITE_URL ?? "";
    try {
      const fullUrl = new URL(downloadUrl, base).toString();
      window.open(fullUrl, "_blank");
    } catch (err) {
      // Fallback: attempt to open the provided string directly
      console.error("Invalid download URL:", err);
      window.open(downloadUrl, "_blank");
    }
  };


  // Render
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 group relative ${isUser
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-foreground"
          }`}
      >
        {Array.isArray(message.content) ? (
          renderTimeline(message.content as TimelineStep[])
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {(() => {
              const found = extractDownloadUrl(message.content);
              
              if (found?.url) {
                return (
                  <a
                    href={`${import.meta.env.VITE_URL}/${found.url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 underline block mt-2"
                  >
                    🔗 Download Video
                  </a>
                );
              }
              return null;
            })()}
            {message.content}
            
          </p>

        )}

        {/* Download button for assistant messages that include an API download path */}
        {!isUser &&
          typeof message.content === "string" &&
          (() => {
            const found = extractDownloadUrl(message.content);
            if (!found) return null;
            return (
              <div className="mt-3 flex items-center gap-2">
                <button
                  onClick={() => handleDownload(found.url, found.jobId)}
                  disabled={downloading}
                  className="inline-flex items-center gap-2 px-3 py-1 rounded bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
                  title="Download video"
                >
                  <Download className="w-4 h-4" />
                  <span className="text-sm">Download video</span>
                </button>

                {downloading && (
                  <div className="text-sm text-muted-foreground flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>
                      {progress !== null ? `${progress}%` : "Downloading..."}
                    </span>
                  </div>
                )}

                {downloadError && (
                  <div className="text-sm text-red-500">{downloadError}</div>
                )}
              </div>
            );
          })()}

        {!isUser && typeof message.content === "string" && (
          <button
            onClick={handleCopy}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-accent rounded"
            title="Copy message"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <Copy className="w-4 h-4" />
            )}
          </button>
        )}
      </div>
    </div>
  );
}
