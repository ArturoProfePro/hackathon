import { useState } from 'react';
import { ChatWindow } from './Components/ChatWindow';
import { MessageInput } from './Components/MessageInput';
import { FileUploader } from './Components/FileUploader';
import { sendMessage, uploadPdf } from './api/api';

function App() {
  const [messages, setMessages] = useState([]);

  const addMessage = (role, text) => {
    setMessages((prev) => [...prev, { role, text }]);
  };

  const handleSend = async (text) => {
    addMessage('user', text);

    const res = await sendMessage(text);
    addMessage('bot', res.reply);
  };

  const handleUpload = async (file, setProgress) => {
    addMessage('user', `📄 Загружен PDF: ${file.name}`);

    const res = await uploadPdf(file, (percent) => {
      setProgress(percent);
    });

    addMessage('bot', res.reply);
  };

  return (
    <div className="max-w-3xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-6 text-center">
        ChatBot with PDF Upload
      </h1>

      <ChatWindow messages={messages} />
      <MessageInput onSend={handleSend} />
      <FileUploader onUpload={handleUpload} />
    </div>
  );
}

export default App;
