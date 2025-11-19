import { MessageInput } from './MessageInput';
import { useRef, useEffect } from 'react';
import { FileUploader } from './FileUploader';

export const ChatWindow = ({ messages, handleUpload, handleSend }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <>
      <div className="flex flex-col h-screen relative bg-transparent">
        <div className="mt-10">
          <FileUploader onUpload={handleUpload} />
        </div>
        <div className="flex-1 w-full overflow-y-auto custom-scroll pb-32 pt-16 ">
          <div className="max-w-3xl mx-auto px-4 mt-5 space-y-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`mb-3 p-3 rounded-xl max-w-[70%] wrap-break-words ${
                  m.role === 'user'
                    ? 'bg-[rgb(48,48,48)] text-white ml-auto'
                    : 'bg-white text-black border'
                }`}
              >
                {m.text}
              </div>
            ))}
            <div ref={bottomRef}></div>
          </div>
        </div>

        <MessageInput onSend={handleSend} />
      </div>
    </>
  );
};
