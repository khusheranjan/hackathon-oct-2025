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

/**
 * ChatContainer:
 * - Manages messages & loading state
 * - Sends prompt to /api/generate
 * - Polls /api/status/:job_id and updates a timeline message
 *
 * Exposes clearMessages() via ref so a parent Header can clear the chat.
 */
const ChatContainer: ForwardRefRenderFunction<ChatContainerHandle, Props> = (
  _props,
  ref
) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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

    // Insert user message
    setMessages((prev) => [...prev, userMsg]);

    // Prepare timeline message and insert
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
      // Call the backend to start a job
      const resp = await fetch("/api/generate", {
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

      // Update timeline: queued -> processing
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

      // start polling the job status
      const poll = async () => {
        try {
          const statusResp = await fetch(`/api/status/${jobId}`);
          if (!statusResp.ok) {
            if (statusResp.status === 404) {
              // job not found
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
            }
            return;
          }
          const statusJson = await statusResp.json();
          const status = statusJson.status;

          if (status === "queued") {
            // still queued
            // already marked queued completed earlier
          } else if (status === "processing") {
            // mark first pending step as processing
            setMessages((prev) =>
              prev.map((m) => {
                if (m.role !== "timeline") return m;
                const steps = [...(m.content as TimelineStep[])];
                // find first step with status pending and mark previous ones completed
                let firstPendingIndex = steps.findIndex(
                  (s) => s.status === "pending"
                );
                if (firstPendingIndex === -1) {
                  // none pending: pick last
                  firstPendingIndex = steps.length - 1;
                }
                // mark all before firstPendingIndex as completed
                for (let i = 0; i < firstPendingIndex; i++)
                  steps[i].status = "completed";
                // set the active one to processing (if not already)
                steps[firstPendingIndex].status = "processing";
                return { ...m, content: steps as TimelineStep[] };
              })
            );
          } else if (status === "completed") {
            // fetch results and mark all completed
            const results = statusJson.results || {};
            setMessages((prev) =>
              prev.map((m) => {
                if (m.role !== "timeline") return m;
                const steps = markAllCompleted(m.content as TimelineStep[]);
                return { ...m, content: steps };
              })
            );

            // Add assistant final message with download link if available
            const assistantContentParts: string[] = [];
            assistantContentParts.push("Video generation completed.");
            if (results.final_video) {
              // our backend download route is /api/download/<job_id>
              assistantContentParts.push(
                `You can download the video here: /api/download/${jobId}`
              );
            } else {
              assistantContentParts.push(
                "No final_video field returned. Check server logs or job results."
              );
            }

            const assistantMsg: Message = {
              id: uuidv4(),
              role: "assistant",
              content: assistantContentParts.join("\n\n"),
              timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, assistantMsg]);
            setIsLoading(false);
            return; // stop polling
          } else if (status === "failed") {
            // mark timeline as failed
            setMessages((prev) =>
              prev.map((m) =>
                m.role === "timeline"
                  ? {
                      ...m,
                      content: (m.content as TimelineStep[]).map((s) =>
                        s.status === "processing"
                          ? { ...s, status: "failed" }
                          : s
                      ) as TimelineStep[],
                    }
                  : m
              )
            );

            const errMsg: Message = {
              id: uuidv4(),
              role: "assistant",
              content: `Video generation failed: ${
                statusJson.error || "Unknown error"
              }`,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errMsg]);
            setIsLoading(false);
            return;
          }
        } catch (err) {
          console.error("Polling error", err);
        }
        // schedule next poll if still loading
        if (isLoading) {
          setTimeout(poll, 2000);
        }
      };

      // small delay then start polling
      setTimeout(poll, 1500);
    } catch (err: any) {
      console.error("Send prompt error", err);
      // update timeline to failed
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
        content: `Failed to start video generation: ${err.message || err}`,
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
      <div className="flex-1 overflow-y-auto">
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
