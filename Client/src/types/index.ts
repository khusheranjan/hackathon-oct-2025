export type Role = "user" | "assistant" | "system" | "timeline";

export type TimelineStep = {
  key: string;
  title: string;
  status: "pending" | "queued" | "processing" | "completed" | "failed";
  detail?: string;
  timestamp?: string;
};

export interface Message {
  id: string;
  role: Role;
  // Use string for timestamp to make it easy to JSON-serialize / deserialize.
  timestamp?: string;
  content: string | TimelineStep[];
}
