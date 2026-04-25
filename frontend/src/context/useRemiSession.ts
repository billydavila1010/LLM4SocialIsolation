import { useContext } from "react";
import { RemiSessionContext } from "./RemiSessionContext";

export function useRemiSession() {
  const context = useContext(RemiSessionContext);

  if (!context) {
    throw new Error("useRemiSession must be used inside RemiSessionProvider");
  }

  return context;
}
