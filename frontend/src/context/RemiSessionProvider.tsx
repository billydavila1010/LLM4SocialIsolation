import { useMemo, useState, type ReactNode } from "react";
import { getMockRemiResponse, getMockWelcomeMessage } from "../api/mockRemiApi";
import type { ChatMessage, SessionSetup } from "../types/chat";
import { RemiSessionContext } from "./RemiSessionContext";

function createMessage(
  role: ChatMessage["role"],
  content: string,
): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    timestamp: new Date().toISOString(),
  };
}

type RemiSessionProviderProps = {
  children: ReactNode;
};

export function RemiSessionProvider({ children }: RemiSessionProviderProps) {
  const [setup, setSetup] = useState<SessionSetup>({
    participantName: "",
    consentAccepted: false,
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isRemiThinking, setIsRemiThinking] = useState(false);

  const apiModeLabel = "Demo Mode";

  async function startSession() {
    setIsRemiThinking(true);

    const welcome = await getMockWelcomeMessage();

    setMessages([
      createMessage(
        "system",
        "Demo Mode is active. Responses are mocked while the backend/OpenAI key is unavailable.",
      ),
      createMessage("remi", welcome),
    ]);

    setIsRemiThinking(false);
  }

  async function sendMessage() {
    const trimmed = inputValue.trim();

    if (!trimmed || isRemiThinking) {
      return;
    }

    setMessages((prev) => [...prev, createMessage("user", trimmed)]);
    setInputValue("");
    setIsRemiThinking(true);

    try {
      const remiResponse = await getMockRemiResponse(trimmed);
      setMessages((prev) => [...prev, createMessage("remi", remiResponse)]);
    } catch {
      setMessages((prev) => [
        ...prev,
        createMessage(
          "system",
          "Something went wrong while getting Remi's response. Please try again.",
        ),
      ]);
    } finally {
      setIsRemiThinking(false);
    }
  }

  function downloadTranscript() {
    const transcript = {
      session: setup,
      messages,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(transcript, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "remi-session-transcript.json";
    link.click();

    URL.revokeObjectURL(url);
  }

  function resetSession() {
    setSetup({
      participantName: "",
      consentAccepted: false,
    });

    setMessages([]);
    setInputValue("");
  }

  const value = useMemo(
    () => ({
      setup,
      messages,
      inputValue,
      isRemiThinking,
      apiModeLabel,
      setSetup,
      setInputValue,
      startSession,
      sendMessage,
      downloadTranscript,
      resetSession,
    }),
    [setup, messages, inputValue, isRemiThinking],
  );

  return (
    <RemiSessionContext.Provider value={value}>
      {children}
    </RemiSessionContext.Provider>
  );
}
