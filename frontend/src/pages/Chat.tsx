// frontend/src/pages/Chat.tsx
import React, { useState, FormEvent } from "react";
import { Send, Ticket, MessageSquare, CheckCircle, Clock } from "lucide-react";

interface ChatMessage {
  user: string;
  message: string;
}

interface Ticket {
  user?: string;
  subject: string;
  description: string;
  priority: "low" | "medium" | "high";
}

export default function Chat() {
  // Chat state
  const [chatMessage, setChatMessage] = useState<string>("");
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);

  // Ticket state
  const [ticket, setTicket] = useState<Ticket>({ subject: "", description: "", priority: "low" });
  const [tickets, setTickets] = useState<Ticket[]>([]);

  // Handle chat submit
  const handleChatSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const newMessage: ChatMessage = { user: "User", message: chatMessage };

    try {
      await fetch("https://customer-sentiment-te99.onrender.com/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newMessage),
        mode: "cors"
      });

      setChatLog([...chatLog, newMessage]);
      setChatMessage("");
    } catch (error) {
      console.error("Error sending chat message:", error);
    }
  };

  // Handle ticket submit
  const handleTicketSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!ticket.subject || !ticket.description) return;

    try {
      await fetch("https://customer-sentiment-te99.onrender.com/api/ticket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ticket),
      });

      setTickets([...tickets, ticket]);
      setTicket({ subject: "", description: "", priority: "low" });
    } catch (error) {
      console.error("Error submitting ticket:", error);
    }
  };

  // Function to get priority color
  const getPriorityColor = (priority: "low" | "medium" | "high") => {
    switch (priority) {
      case 'low':
        return 'bg-green-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'high':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen p-8 bg-slate-900 text-white flex justify-center items-start">
      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chat Section */}
        <div className="bg-slate-800 rounded-3xl shadow-xl border border-slate-700 p-6 flex flex-col">
          <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
            <MessageSquare className="text-blue-400" size={32} />
            Real-time Chat
          </h2>
          <div className="flex-1 overflow-y-auto mb-6 p-4 rounded-xl bg-slate-700/50 border border-slate-600 space-y-4">
            {chatLog.map((msg, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg max-w-[85%] ${
                  msg.user === "User"
                    ? "bg-blue-600 text-white ml-auto"
                    : "bg-gray-200 text-gray-900 mr-auto"
                }`}
              >
                <span className="font-semibold">{msg.user}:</span> {msg.message}
              </div>
            ))}
          </div>
          <form onSubmit={handleChatSubmit} className="flex gap-4">
            <input
              type="text"
              className="flex-1 bg-slate-700 border-2 border-slate-600 rounded-xl p-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="Type a message..."
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
            />
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors duration-200"
            >
              <Send size={20} />
            </button>
          </form>
        </div>

        {/* Ticket Section */}
        <div className="bg-slate-800 rounded-3xl shadow-xl border border-slate-700 p-6 flex flex-col">
          <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
            <Ticket className="text-green-400" size={32} />
            Submit a Ticket
          </h2>
          <form onSubmit={handleTicketSubmit} className="space-y-4">
            <input
              type="text"
              className="w-full bg-slate-700 border-2 border-slate-600 rounded-xl p-3 text-white placeholder-slate-400 focus:outline-none focus:border-green-500 transition-colors"
              placeholder="Subject"
              value={ticket.subject}
              onChange={(e) => setTicket({ ...ticket, subject: e.target.value })}
            />
            <textarea
              className="w-full bg-slate-700 border-2 border-slate-600 rounded-xl p-3 text-white placeholder-slate-400 focus:outline-none focus:border-green-500 transition-colors resize-none"
              placeholder="Description"
              rows={4}
              value={ticket.description}
              onChange={(e) => setTicket({ ...ticket, description: e.target.value })}
            />
            <div className="space-y-2">
              <label htmlFor="priority" className="text-sm font-medium text-slate-400">
                Priority:
              </label>
              <select
                id="priority"
                className="w-full bg-slate-700 border-2 border-slate-600 rounded-xl p-3 text-white focus:outline-none focus:border-green-500 transition-colors"
                value={ticket.priority}
                onChange={(e) => setTicket({ ...ticket, priority: e.target.value as Ticket['priority'] })}
              >
                <option className="bg-slate-700 text-green-400" value="low">Low</option>
                <option className="bg-slate-700 text-yellow-400" value="medium">Medium</option>
                <option className="bg-slate-700 text-red-400" value="high">High</option>
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 transform hover:scale-105"
            >
              Submit Ticket
            </button>
          </form>

          {/* Show submitted tickets */}
          <div className="mt-8">
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <CheckCircle className="text-green-400" size={24} />
              Submitted Tickets
            </h3>
            {tickets.length === 0 ? (
              <p className="text-slate-400 italic">No tickets have been submitted yet.</p>
            ) : (
              <div className="space-y-4 max-h-64 overflow-y-auto">
                {tickets.map((t, idx) => (
                  <div key={idx} className="bg-slate-700 rounded-xl p-4 border border-slate-600 shadow-sm">
                    <p className="font-semibold text-lg">{t.subject}</p>
                    <p className="text-slate-300 mt-1 text-sm">{t.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`w-3 h-3 rounded-full ${getPriorityColor(t.priority)}`}></span>
                      <span className="text-xs font-medium text-slate-400">
                        Priority: {t.priority.charAt(0).toUpperCase() + t.priority.slice(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
