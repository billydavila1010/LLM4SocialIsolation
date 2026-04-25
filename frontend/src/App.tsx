import { Navigate, Route, Routes } from "react-router-dom";
import { useRemiSession } from "./context/useRemiSession";
import { ChatPage } from "./pages/ChatPage";
import { LandingPage } from "./pages/LandingPage";
import { SessionSetupPage } from "./pages/SessionSetupPage";
import { SessionSummaryPage } from "./pages/SessionSummaryPage";

function ProtectedSessionRoute({ children }: { children: React.ReactNode }) {
  const { setup } = useRemiSession();

  if (!setup.consentAccepted) {
    return <Navigate to="/setup" replace />;
  }

  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/setup" element={<SessionSetupPage />} />

      <Route
        path="/session"
        element={
          <ProtectedSessionRoute>
            <ChatPage />
          </ProtectedSessionRoute>
        }
      />

      <Route path="/summary" element={<SessionSummaryPage />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
