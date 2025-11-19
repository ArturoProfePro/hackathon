export const ChatWindow = ({ messages }) => {
  return (
    <div className="h-[70vh] overflow-y-auto p-4 border rounded-xl bg-gray-50">
      {messages.map((m, i) => (
        <div
          key={i}
          className={`mb-3 p-3 rounded-xl max-w-[70%] ${
            m.role === 'user'
              ? 'bg-blue-500 text-white ml-auto'
              : 'bg-white border'
          }`}
        >
          {m.text}
        </div>
      ))}
    </div>
  );
};
