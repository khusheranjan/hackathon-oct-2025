import { forwardRef, useImperativeHandle, useState } from "react";
import type { ForwardRefRenderFunction } from "react";
import { v4 as uuidv4 } from "uuid";

import type { Message, TimelineStep } from "../../types";
import ChatArea from "./chatArea";
import InputArea from "./inputArea";

export type ChatContainerHandle = {
  clearMessages: () => void;
};

type Props = {};
const ChatContainer: ForwardRefRenderFunction<ChatContainerHandle, Props> = (
  _props,
  ref
) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const API_BASE_URL = import.meta.env.VITE_URL;

  const generateInitialTimeline = (): TimelineStep[] => {
    const now = new Date().toISOString();
    return [
      { key: "queued", title: "Job queued", status: "queued", timestamp: now },
      {
        key: "scene_breakdown",
        title: "Generating scene breakdown",
        status: "pending",
      },
      {
        key: "manim_code",
        title: "Generating timed Manim code",
        status: "pending",
      },
      {
        key: "narration_audio",
        title: "Generating narration audio",
        status: "pending",
      },
      { key: "concat_audio", title: "Concatenating audio", status: "pending" },
      { key: "subtitles", title: "Generating subtitles", status: "pending" },
      {
        key: "rendering",
        title: "Rendering Manim animation",
        status: "pending",
      },
      { key: "sync", title: "Syncing animation with audio", status: "pending" },
      {
        key: "add_subtitles",
        title: "Adding subtitles to video",
        status: "pending",
      },
      { key: "finalizing", title: "Finalizing video", status: "pending" },
    ];
  };

  const updateTimelineStatus = (
    timeline: TimelineStep[],
    key: string,
    status: TimelineStep["status"],
    detail?: string
  ) => {
    return timeline.map((s) =>
      s.key === key
        ? { ...s, status, detail, timestamp: new Date().toISOString() }
        : s
    );
  };

  const markAllCompleted = (timeline: TimelineStep[]): TimelineStep[] =>
    timeline.map((s) => ({
      ...s,
      status: "completed" as const,
      timestamp: s.timestamp ?? new Date().toISOString(),
    }));

  // expose imperative handle to parent
  useImperativeHandle(ref, () => ({
    clearMessages: () => {
      setMessages([]);
      setIsLoading(false);
    },
  }));

  const sendPrompt = async (description: string) => {
  if (!description.trim()) return;

  const userMsg: Message = {
    id: uuidv4(),
    role: "user",
    content: description,
    timestamp: new Date().toISOString(),
  };

  setMessages((prev) => [...prev, userMsg]);

  const timelineSteps = generateInitialTimeline();
  const timelineMsg: Message = {
    id: uuidv4(),
    role: "timeline",
    content: timelineSteps,
    timestamp: new Date().toISOString(),
  };

  setMessages((prev) => [...prev, timelineMsg]);
  setIsLoading(true);

  try {
    // 🚀 Start generation
    const resp = await fetch(`${API_BASE_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      throw new Error(`Generate API failed: ${errText}`);
    }

    const json = await resp.json();
    const jobId: string = json.job_id;
    localStorage.setItem("job_id", jobId);

    // Mark queued complete
    setMessages((prev) =>
      prev.map((m) =>
        m.role === "timeline"
          ? {
              ...m,
              content: updateTimelineStatus(
                m.content as any,
                "queued",
                "completed"
              ) as TimelineStep[],
            }
          : m
      )
    );

    // 🕒 Poll for job status every 2 seconds
    const pollInterval = setInterval(async () => {
      try {
        const statusResp = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        if (!statusResp.ok) {
          if (statusResp.status === 404) {
            setMessages((prev) =>
              prev.map((m) =>
                m.role === "timeline"
                  ? {
                      ...m,
                      content: updateTimelineStatus(
                        m.content as any,
                        "queued",
                        "failed",
                        "Job not found on server"
                      ) as TimelineStep[],
                    }
                  : m
              )
            );
            setIsLoading(false);
            clearInterval(pollInterval);
          }
          return;
        }

        const statusJson = await statusResp.json();
        const status = statusJson.status;

        if (status === "queued" || status === "processing") {
          // Update timeline progress
          setMessages((prev) =>
            prev.map((m) => {
              if (m.role !== "timeline") return m;
              const steps = [...(m.content as TimelineStep[])];
              const firstPendingIndex = steps.findIndex(
                (s) => s.status === "pending"
              );

              if (firstPendingIndex !== -1) {
                // Mark all before pending as completed
                for (let i = 0; i < firstPendingIndex; i++) {
                  steps[i].status = "completed";
                }
                // Mark current one as processing
                steps[firstPendingIndex].status = "processing";
              }

              return { ...m, content: steps };
            })
          );
        }

        else if (status === "completed") {
          const results = statusJson.results || {};
          clearInterval(pollInterval);

          // Mark all as done
          setMessages((prev) =>
            prev.map((m) =>
              m.role === "timeline"
                ? { ...m, content: markAllCompleted(m.content as TimelineStep[]) }
                : m
            )
          );

          const assistantMsg: Message = {
            id: uuidv4(),
            role: "assistant",
            content: results.final_video
              ? `✅ Video generated successfully!\n\n[Download Video](${API_BASE_URL}/api/download/${jobId})`
              : "✅ Video generated, but no final file found in results.",
            timestamp: new Date().toISOString(),
          };

          setMessages((prev) => [...prev, assistantMsg]);
          setIsLoading(false);
        }

        else if (status === "failed") {
          clearInterval(pollInterval);
          setMessages((prev) =>
            prev.map((m) =>
              m.role === "timeline"
                ? {
                    ...m,
                    content: (m.content as TimelineStep[]).map((s) =>
                      s.status === "processing"
                        ? { ...s, status: "failed" }
                        : s
                    ),
                  }
                : m
            )
          );

          const errMsg: Message = {
            id: uuidv4(),
            role: "assistant",
            content: `❌ Video generation failed: ${
              statusJson.error || "Unknown error"
            }`,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, errMsg]);
          setIsLoading(false);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);
  } catch (err: any) {
    console.error("Send prompt error", err);
    setMessages((prev) =>
      prev.map((m) =>
        m.role === "timeline"
          ? {
              ...m,
              content: (m.content as TimelineStep[]).map((s) => ({
                ...s,
                status: "failed",
              })) as TimelineStep[],
            }
          : m
      )
    );

    const assistantMsg: Message = {
      id: uuidv4(),
      role: "assistant",
      content: `❌ Failed to start video generation: ${err.message || err}`,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, assistantMsg]);
    setIsLoading(false);
  }
};


  return (
    // Use h-full so the page-level container controls viewport height. This lets sticky/flex behave correctly.
    <div className="flex flex-col h-full mt-16">
      {/* ChatArea grows and scrolls */}
      <div className="flex-1 overflow-y-auto mb-16">
        <ChatArea messages={messages} isLoading={isLoading} />
      </div>

      {/* Input area pinned to bottom of this container (sticky requires ancestor height) */}
      <div className="sticky bottom-0 z-20 bg-background border-t border-border">
        <InputArea onSendMessage={sendPrompt} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default forwardRef(ChatContainer);
