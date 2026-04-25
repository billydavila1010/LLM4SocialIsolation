import { useNavigate } from "react-router-dom";
import { useRemiSession } from "../context/useRemiSession";
import { buttons, forms, layout, text } from "../styles/classes";

export function SessionSetupPage() {
  const navigate = useNavigate();
  const { setup, setSetup, startSession, isRemiThinking } = useRemiSession();

  async function handleBeginConversation() {
    if (!setup.consentAccepted || isRemiThinking) {
      return;
    }

    await startSession();
    navigate("/session");
  }

  return (
    <main className={layout.page}>
      <section className={layout.card}>
        <button className={buttons.text} onClick={() => navigate("/")}>
          ← Back
        </button>

        <h1 className={text.h2}>Session Setup</h1>

        <p className={text.muted}>
          Add an optional name or nickname before beginning your Remi session.
          Remi will guide the conversation from there.
        </p>

        <label className={forms.label}>
          Participant name
          <input
            className={forms.input}
            value={setup.participantName}
            onChange={(event) => {
              setSetup((prev) => ({
                ...prev,
                participantName: event.target.value,
              }));
            }}
            placeholder="Optional"
          />
        </label>

        <label className={forms.checkboxLabel}>
          <input
            className={forms.checkbox}
            type="checkbox"
            checked={setup.consentAccepted}
            onChange={(event) => {
              setSetup((prev) => ({
                ...prev,
                consentAccepted: event.target.checked,
              }));
            }}
          />
          <span>
            I understand Remi is not a medical provider and is not for
            emergencies.
          </span>
        </label>

        <button
          className={buttons.primary}
          disabled={!setup.consentAccepted || isRemiThinking}
          onClick={handleBeginConversation}
        >
          {isRemiThinking ? "Starting ..." : "Begin Conversation"}
        </button>
      </section>
    </main>
  );
}
