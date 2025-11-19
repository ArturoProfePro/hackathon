import { useState } from 'react';
import { ArrowBigUp } from 'lucide-react';
export const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message);
    setMessage('');
  };

  return (
    <div className="fixed bottom-0 left-0 w-full z-20 bg-transparent p-4">
      <div className="max-w-3xl mx-auto flex gap-2 items-center relative">
        <input
          className="flex-1 p-3 rounded-full bg-[#303030] h-15 transition-all duration-333 ease-in  hover:ring-2 hover:ring-amber-400 text-amber-500
                 focus:outline-none focus:ring-2 focus:ring-amber-500"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Message Creator of the Lecture..."
        />

        <button
          onClick={handleSend}
          className="w-15 h-15 cursor-pointer hover:scale-110 hover:bg-amber-400 transition-all duration-666 ease-in-out bg-amber-500 text-white rounded-full shadow flex items-center justify-center"
        >
          <ArrowBigUp />
        </button>
      </div>
    </div>
  );
};
