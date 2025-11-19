import { useState } from 'react';
import { ChatWindow } from './Components/ChatWindow';
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
    <>
      <div className="h-screen overflow-hidden">
        <h1 className="text-2xl  whitespace-nowrap fixed z-10 top-0 w-full hover bg-[#212121] font-mono  text-white py-2 px-4 border-b border-white/10">
          <div className="w-3.5 hover:w-full transition-all duration-666 animate-bounce hover:animate-none ease-in-out overflow-hidden">
            Creator of the Lecture
          </div>
        </h1>
        <div className="max-w-3xl overflow-y-auto h-full  mx-auto ">
          <ChatWindow
            messages={messages}
            handleUpload={handleUpload}
            handleSend={handleSend}
          />
          {/* <FileUploader onUpload={handleUpload} /> */}
        </div>
      </div>
    </>
  );
}

export default App;
