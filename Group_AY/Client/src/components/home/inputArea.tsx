import type React from "react";
import { useState, useRef, useEffect } from "react";
import { Button } from "../ui/button";
import { Send, User, Video } from "lucide-react";

export interface AvatarOptions {
  addAvatar: boolean;
  avatarPosition: "bottom-right" | "bottom-left" | "top-right" | "top-left";
  useSimpleAvatar: boolean;
}

interface InputAreaProps {
  onSendMessage: (message: string, avatarOptions: AvatarOptions) => void;
  isLoading: boolean;
}

export default function InputArea({
  onSendMessage,
  isLoading,
}: InputAreaProps) {
  const [input, setInput] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [avatarOptions, setAvatarOptions] = useState<AvatarOptions>({
    addAvatar: false,
    avatarPosition: "bottom-right",
    useSimpleAvatar: false, // Use D-ID by default (advanced talking avatar)
  });
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input, avatarOptions);
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="border-t border-border bg-background fixed left-0 right-0 bottom-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-4">
        {/* Avatar Options Toggle */}
        <div className="mb-3">
          <button
            type="button"
            onClick={() => setShowOptions(!showOptions)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            disabled={isLoading}
          >
            <Video className="w-4 h-4" />
            <span>Avatar Options</span>
            <span className="text-xs">{showOptions ? "▲" : "▼"}</span>
          </button>

          {showOptions && (
            <div className="mt-3 p-3 border border-border rounded-lg bg-muted/30 space-y-3">
              {/* Add Avatar Toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={avatarOptions.addAvatar}
                  onChange={(e) =>
                    setAvatarOptions({
                      ...avatarOptions,
                      addAvatar: e.target.checked,
                    })
                  }
                  disabled={isLoading}
                  className="w-4 h-4 rounded border-input"
                />
                <User className="w-4 h-4 text-primary" />
                <span className="text-sm">Add Avatar to Video</span>
              </label>

              {/* Avatar Position */}
              {avatarOptions.addAvatar && (
                <div className="space-y-2 pl-6">
                  <label className="block text-sm text-muted-foreground">
                    Avatar Position:
                  </label>
                  <select
                    value={avatarOptions.avatarPosition}
                    onChange={(e) =>
                      setAvatarOptions({
                        ...avatarOptions,
                        avatarPosition: e.target.value as any,
                      })
                    }
                    disabled={isLoading}
                    className="w-full px-3 py-2 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="bottom-right">Bottom Right</option>
                    <option value="bottom-left">Bottom Left</option>
                    <option value="top-right">Top Right</option>
                    <option value="top-left">Top Left</option>
                  </select>

                  {/* Avatar Type */}
                  <div className="space-y-2 mt-2">
                    <label className="block text-sm text-muted-foreground">
                      Avatar Type:
                    </label>
                    <div className="space-y-2">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="avatarType"
                          checked={!avatarOptions.useSimpleAvatar}
                          onChange={() =>
                            setAvatarOptions({
                              ...avatarOptions,
                              useSimpleAvatar: false,
                            })
                          }
                          disabled={isLoading}
                          className="w-4 h-4"
                        />
                        <div className="flex-1">
                          <span className="text-sm font-medium">
                            🎭 Realistic Talking Avatar (D-ID)
                          </span>
                          <p className="text-xs text-muted-foreground">
                            Lip-synced, professional quality - Recommended
                          </p>
                        </div>
                      </label>

                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="avatarType"
                          checked={avatarOptions.useSimpleAvatar}
                          onChange={() =>
                            setAvatarOptions({
                              ...avatarOptions,
                              useSimpleAvatar: true,
                            })
                          }
                          disabled={isLoading}
                          className="w-4 h-4"
                        />
                        <div className="flex-1">
                          <span className="text-sm">
                            🖼️ Simple Avatar (DALL-E)
                          </span>
                          <p className="text-xs text-muted-foreground">
                            Static image with subtle animation - Faster & cheaper
                          </p>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here... (Shift+Enter for new line)"
            disabled={isLoading}
            className="flex-1 resize-none bg-input border border-input rounded-lg px-4 py-3 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed max-h-32"
            rows={1}
          />
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="self-end"
            size="icon"
          >
            <Send className="w-5 h-5" />
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2">
          💡 Tip: Press Shift+Enter for a new line
          {avatarOptions.addAvatar && (
            <span className="ml-2 text-primary">
              • Avatar enabled ({avatarOptions.useSimpleAvatar ? "Simple" : "D-ID Talking"})
            </span>
          )}
        </p>
      </div>
    </div>
  );
}
