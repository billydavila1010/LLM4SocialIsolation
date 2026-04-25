import { useNavigate } from "react-router-dom";
import { badges, buttons, layout, notices, text } from "../styles/classes";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <main className={layout.page}>
      <section className={layout.card}>
        <div className={badges.default}>Reminiscence Therapy Assistant</div>

        <h1 className={text.h1}> Remi </h1>

        <p className={text.hero}>
          Remi is a conversation assistant designed to guide reflective,
          memory-based conversations in a calm and supportive way.
        </p>

        <div className={notices.safety}>
          <strong>Safety note:</strong> Remi is not a doctor, emergency service,
          or replacement for professional care.
        </div>

        <button className={buttons.primary} onClick={() => navigate("/setup")}>
          Start Session
        </button>
      </section>
    </main>
  );
}
