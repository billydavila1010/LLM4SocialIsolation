const mockResponses = [
  "Thank you for sharing that. Could you tell me a little more about what made that memory meaningful for you?",
  "That sounds like an important memory. What emotions come up for you as you think about it now?",
  "I appreciate you sharing that with me. Who else was part of that moment?",
  "That memory seems connected to a meaningful part of your life. What would you want someone else to understand about it?",
  "Thank you. As we reflect on this, what stands out as the most valuable part of that experience?",
];

let responseIndex = 0;

export async function getMockRemiResponse(
  userMessage: string,
): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const lowerMessage = userMessage.toLowerCase();

      if (lowerMessage.includes("sad") || lowerMessage.includes("lonely")) {
        resolve(
          "I'm sorry you're feeling that way. We can go slowly. Is there a memory, person, place, or time in your life that feels comforting to think about?",
        );
        return;
      }

      if (lowerMessage.includes("bye") || lowerMessage.includes("stop")) {
        resolve(
          "Thank you for spending this time reflecting with me. I hope this conversation helped bring forward a meaningful memory.",
        );
        return;
      }

      const response = mockResponses[responseIndex % mockResponses.length];
      responseIndex += 1;
      resolve(response);
    }, 900);
  });
}

export async function getMockWelcomeMessage(): Promise<string> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(
        "Hello, I’m Remi, a reminiscence therapy conversation assistant. I’m here to help you reflect on meaningful memories in a calm and supportive way. To begin, could you share three words that describe how you are feeling today?",
      );
    }, 500);
  });
}
