export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

// TODO: Add API integration types here
// export interface APIConfig {
//   endpoint: string
//   apiKey: string
//   model?: string
// }
