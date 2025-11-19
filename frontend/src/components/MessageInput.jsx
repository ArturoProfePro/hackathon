import { useState } from 'react';

export const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message);
    setMessage('');
  };

  return (
    <div className="flex gap-2 mt-3">
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="grow p-2 border rounded-xl"
        placeholder="Введите сообщение..."
      />
      <button
        onClick={handleSend}
        className="bg-blue-600 text-white px-4 py-2 rounded-xl"
      >
        Send
      </button>
    </div>
  );
};
