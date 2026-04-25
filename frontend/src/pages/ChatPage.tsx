import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import { useRemiSession } from "../context/useRemiSession";
import { badges, buttons, layout } from "../styles/classes";
import type { ChatMessage } from "../types/chat";

function getSpeakerLabel(message: ChatMessage, participantName: string) {
  if (message.role === "user") {
    return participantName || "You";
  } else if (message.role === "remi") {
    return "Remi";
  }

  return "System";
}

export function ChatPage() {
  const navigate = useNavigate();
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const {
    setup,
    messages,
    inputValue,
    isRemiThinking,
    apiModeLabel,
    setInputValue,
    sendMessage,
  } = useRemiSession();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isRemiThinking]);

  function handleEndSession() {
    navigate("/summary");
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <main className={layout.chatPage}>
      <header className="flex flex-col gap-4 border-b border-stone-200 bg-white/90 px-4 py-5 sm:px-8 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-stone-900"> Remi</h1>
          <p className="mt-1 text-stone-600">
            Reminiscence Therapy Conversation
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="rounded-2xl bg-amber-50 px-4 py-3 text-sm font-bold text-amber-900 ring-1 ring-amber-200"
            type="button"
          >
            {" "}
            Post-session survey
          </button>
          <span
            className={
              apiModeLabel === "Demo Mode" ? badges.demo : badges.backend
            }
          >
            {apiModeLabel}
          </span>

          <button className={buttons.secondary} onClick={handleEndSession}>
            End Session
          </button>
        </div>
      </header>

      <section className="mx-auto w-full max-w-5xl space-y-4 overflow-y-auto px-4 py-6 sm:px-8">
        {messages.map((message) => {
          const isUser = message.role === "user";
          const isSystem = message.role === "system";
          return (
            <div
              key={message.id}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[88%] rounded-3xl px-5 py-4 leading-7 shadow-lg sm:max-w-2xl ${
                  isUser
                    ? "rounded-br-md bg-green-800 text-white"
                    : isSystem
                      ? "border border-amber-200 bg-amber-50 text-amber-950"
                      : "rounded-bl-md border border-stone-200 bg-white text-stone-800"
                }`}
              >
                <div className="mb-1 text-sm font-extrabold opacity-80">
                  {getSpeakerLabel(message, setup.participantName)}
                </div>
              </div>
              <p>{message.content} </p>
            </div>
          );
        })}

        {isRemiThinking && (
          <div className="flex justify-start">
            <div className="max-w-[88%] rounded-3xl rounded-bl-md border border-stone-200 bg-white px-5 py-4 leading-7 text-stone-800 shadow-lg sm:max-w-2xl">
              <div className="mb-1 text-sm font-extrabold opacity-80">Remi</div>
              <p>Remi is thinking...</p>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </section>

      <footer className="mx-auto grid w-full max-w-5xl grid-cols-1 gap-3 px-4 pb-5 sm:px-8 md:grid-cols-[1fr_auto]">
        <textarea
          className="min-h-20 resize-none rounded-3xl border border-stone-300 bg-white px-5 py-4 text-stone-900 outline-none transition focus:border-green-800 focus:ring-4 focus:ring-green-800/10"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message to Remi..."
          rows={2}
        />

        <button
          className={`${buttons.primary} md:min-w-28`}
          disabled={!inputValue.trim() || isRemiThinking}
          onClick={sendMessage}
        >
          Send
        </button>
      </footer>
    </main>
  );
}
