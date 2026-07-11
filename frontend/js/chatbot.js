function addBubble(text, from) {
  const container = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble from-${from}`;
  bubble.textContent = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage(mode, message) {
  const userId = USER_ID_MAP[mode];

  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, message }),
    });

    if (!res.ok) return null;
    const data = await res.json();
    return data.reply;
  } catch (e) {
    console.warn("chat request failed", e);
    return null;
  }
}

function initChatbot() {
  const mode = document.body.dataset.financeMode;
  if (!mode) return; // chat panel only exists on dashboard pages

  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");

  const handleSend = async () => {
    const message = input.value.trim();
    if (!message) return;

    addBubble(message, "user");
    input.value = "";

    const reply = await sendChatMessage(mode, message);

    if (!reply) {
      addBubble("I couldn't reach the assistant right now — try again in a moment.", "ai");
      return;
    }

    addBubble(reply, "ai");
  };

  sendBtn.addEventListener("click", handleSend);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSend();
  });
}

document.addEventListener("DOMContentLoaded", initChatbot);