// Simple chat simulation script

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('#chat-form');
  const input = document.querySelector('#message-input');
  const chatBox = document.querySelector('.chat-box');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = input.value.trim();
      if (!message) return;

      // Append user's message
      const msgDiv = document.createElement('div');
      msgDiv.className = 'message user';
      msgDiv.textContent = message;
      chatBox.appendChild(msgDiv);

      // Auto scroll down
      chatBox.scrollTop = chatBox.scrollHeight;
      input.value = '';

      // Simulate bot reply
      setTimeout(() => {
        const reply = document.createElement('div');
        reply.className = 'message other';
        reply.textContent = 'Bot: I received your message.';
        chatBox.appendChild(reply);
        chatBox.scrollTop = chatBox.scrollHeight;
      }, 800);
    });
  }
});
