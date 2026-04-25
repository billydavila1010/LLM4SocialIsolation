export type MessageRole = "user" | "remi" | "system";

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
};

export type SessionSetup = {
  participantName: string;
  consentAccepted: boolean;
};
