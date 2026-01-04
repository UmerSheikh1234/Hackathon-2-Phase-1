"use client";

import { useState, FormEvent } from 'react';
import { sendChatMessage } from '@/lib/api'; // Import the new function

// Define message type for the chat
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);

  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await sendChatMessage(inputMessage, conversationId);
      const assistantMessage: ChatMessage = { role: 'assistant', content: response.response };
      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: ChatMessage = { role: 'assistant', content: "Sorry, I couldn't get a response from the AI." };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-10 bg-gray-800 border border-gray-700 rounded-lg shadow-lg flex flex-col h-[600px]">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold text-center">AI Assistant</h2>
      </div>
      <div className="flex-grow p-4 overflow-y-auto space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2 rounded-lg max-w-xs lg:max-w-md ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'}`}>
              <p>{msg.content}</p>
            </div>
          </div>
        ))}
         {messages.length === 0 && (
            <div className="text-center text-gray-500">
                <p>Ask me to add, list, or complete tasks!</p>
            </div>
        )}
      </div>
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me to do something..."
            className="flex-grow p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}