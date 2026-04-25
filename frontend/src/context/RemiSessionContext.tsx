import { createContext } from "react";
import type { ChatMessage, SessionSetup } from "../types/chat";

export type RemiSessionContextValue = {
  setup: SessionSetup;
  messages: ChatMessage[];
  inputValue: string;
  isRemiThinking: boolean;
  apiModeLabel: string;
  setSetup: React.Dispatch<React.SetStateAction<SessionSetup>>;
  setInputValue: React.Dispatch<React.SetStateAction<string>>;
  startSession: () => Promise<void>;
  sendMessage: () => Promise<void>;
  downloadTranscript: () => void;
  resetSession: () => void;
};

export const RemiSessionContext = createContext<RemiSessionContextValue | null>(
  null,
);
