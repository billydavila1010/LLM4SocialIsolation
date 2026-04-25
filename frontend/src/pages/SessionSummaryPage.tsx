import { useNavigate } from "react-router-dom";
import { useRemiSession } from "../context/useRemiSession";
import { buttons, layout, text } from "../styles/classes";
import type { ChatMessage } from "../types/chat";

function getSpeakerLabel(message: ChatMessage, participantName: string) {
  if (message.role === "user") {
    return participantName || "You";
  } else if (message.role === "remi") {
    return "Remi";
  }

  return "System";
}

export function SessionSummaryPage() {
  const navigate = useNavigate();
  const { setup, messages, downloadTranscript, resetSession } =
    useRemiSession();

  function handleStartNewSession() {
    resetSession();
    navigate("/");
  }

  function handleReturnToChat() {
    navigate("/session");
  }

  return (
    <main className={layout.page}>
      <section className={layout.card}>
        <h1 className={text.h2}> Session Complete</h1>
        <p className={text.muted}>
          {" "}
          Here is the transcript from this Remi session
        </p>
        <div className="my-6 flex flex-wrap gap-3">
          <button className={buttons.primary} onClick={downloadTranscript}>
            Download Transcript
          </button>
          <button className={buttons.secondary} type="button">
            Open Post-session survey
          </button>
          <button className={buttons.secondary} onClick={handleReturnToChat}>
            Return to Chat
          </button>
          <button className={buttons.secondary} onClick={handleStartNewSession}>
            Start New Session
          </button>
        </div>
        {messages.length === 0 ? (
          <div className="mt-6 rounded-3xl border border-stone-200 bg-stone-50 p-5 leading-7 text-stone-700">
            No transcript is available yet. Start a session to generate a
            conversation transcript.
          </div>
        ) : (
          <div className="mt-6 max-h-[430px] overflow-y-auto rounded-3xl border border-stone-200 bg-stone-50 p-5">
            {messages.map((message) => {
              return (
                <div
                  key={message.id}
                  className="border-b border-stone-200 py-3 leading-7 last:border-b-0"
                >
                  <strong>
                    {" "}
                    {getSpeakerLabel(message, setup.participantName)}:{" "}
                  </strong>{" "}
                  {message.content}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
