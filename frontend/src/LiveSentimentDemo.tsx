import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MessageCircle, TrendingUp, AlertTriangle, Smile, Frown, Meh, BarChart3 } from "lucide-react";

const FloatingCard = ({ children, delay = 0 }) => (
  <div
    className="transform hover:scale-105 transition-all duration-700 hover:rotate-1"
    style={{
      animation: `float 6s ease-in-out infinite ${delay}s`,
    }}
  >
    {children}
  </div>
);

const LiveSentimentDemo = () => {
  const [messages, setMessages] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [stats, setStats] = useState({
    positive: 0,
    negative: 0,
    neutral: 0,
    alerts: 0
  });

  const sampleMessages = [
  { customer: "Anjali J.", message: "This service is absolutely terrible! I've been waiting for hours!", emotion: "negative", severity: "high" },
  { customer: "Rohan C.", message: "Thanks for the quick response, really appreciate it!", emotion: "positive", severity: "low" },
  { customer: "Priya D.", message: "I'm confused about how this works, can you help?", emotion: "neutral", severity: "medium" },
  { customer: "Sanjay B.", message: "I'm getting really frustrated with these constant errors!", emotion: "negative", severity: "high" },
  { customer: "Kavya M.", message: "Great product, exactly what I needed!", emotion: "positive", severity: "low" },
  { customer: "Vikram R.", message: "Is there a way to change my subscription?", emotion: "neutral", severity: "low" },
  { customer: "Neha K.", message: "This is the worst experience I've ever had!", emotion: "negative", severity: "high" },
  { customer: "Rajesh L.", message: "Outstanding customer service, thank you!", emotion: "positive", severity: "low" },
];

  useEffect(() => {
    let interval;

    if (isMonitoring) {
      interval = setInterval(() => {
        const randomMessage = sampleMessages[Math.floor(Math.random() * sampleMessages.length)];
        const newMessage = {
          id: Date.now().toString(),
          ...randomMessage,
          timestamp: new Date()
        };

        setMessages(prev => [newMessage, ...prev.slice(0, 9)]);

        setStats(prev => ({
          ...prev,
          [newMessage.emotion]: prev[newMessage.emotion] + 1,
          alerts: newMessage.emotion === 'negative' && newMessage.severity === 'high'
            ? prev.alerts + 1
            : prev.alerts
        }));
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMonitoring]);

  const getEmotionIcon = (emotion) => {
    switch (emotion) {
      case "positive": return <Smile className="w-4 h-4 text-green-400" />;
      case "negative": return <Frown className="w-4 h-4 text-red-400" />;
      default: return <Meh className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getEmotionColor = (emotion) => {
    switch (emotion) {
      case "positive": return "bg-green-500/20 text-green-400 border-green-500/30";
      case "negative": return "bg-red-500/20 text-red-400 border-red-500/30";
      default: return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    }
  };

  return (
    <div className="space-y-8">
      {/* Demo Controls */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-3xl p-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left">
            <div className="flex items-center gap-3 justify-center md:justify-start mb-2">
              <MessageCircle className="w-6 h-6 text-purple-400" />
              <h3 className="text-2xl font-bold text-white">Live Sentiment Monitoring Demo</h3>
            </div>
            <p className="text-gray-300">Watch AI analyze customer messages in real-time and detect emotional sentiment</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={() => setIsMonitoring(!isMonitoring)}
              className={`px-8 py-3 font-bold rounded-xl transition-all duration-300 hover:scale-105 ${
                isMonitoring 
                  ? "bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-red-500/25" 
                  : "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-purple-500/25"
              }`}
            >
              {isMonitoring ? "Stop Monitoring" : "Start Live Demo"}
            </Button>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isMonitoring ? "bg-green-500 animate-pulse" : "bg-gray-500"}`}></div>
              <span className="text-sm text-gray-300">
                {isMonitoring ? "Monitoring Active" : "Monitoring Stopped"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[
          { icon: Smile, label: "Positive", value: stats.positive, color: "text-green-400", bg: "from-green-500/20 to-green-600/20" },
          { icon: Frown, label: "Negative", value: stats.negative, color: "text-red-400", bg: "from-red-500/20 to-red-600/20" },
          { icon: Meh, label: "Neutral", value: stats.neutral, color: "text-yellow-400", bg: "from-yellow-500/20 to-yellow-600/20" },
          { icon: AlertTriangle, label: "Alerts", value: stats.alerts, color: "text-orange-400", bg: "from-orange-500/20 to-orange-600/20" }
        ].map((stat, index) => (
          <FloatingCard key={stat.label} delay={index * 0.1}>
            <div className={`bg-gradient-to-br ${stat.bg} backdrop-blur-xl border border-white/20 rounded-2xl p-6 text-center hover:scale-105 transition-all duration-300`}>
              <stat.icon className={`w-8 h-8 ${stat.color} mx-auto mb-3`} />
              <div className={`text-3xl font-bold ${stat.color} mb-1`}>{stat.value}</div>
              <div className="text-gray-300 text-sm">{stat.label}</div>
            </div>
          </FloatingCard>
        ))}
      </div>

      {/* Live Message Feed */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-3xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <BarChart3 className="w-6 h-6 text-purple-400" />
          <h3 className="text-xl font-bold text-white">Live Message Analysis</h3>
          {isMonitoring && (
            <div className="flex items-center gap-2 ml-auto">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
              <span className="text-green-400 text-sm font-medium">Processing...</span>
            </div>
          )}
        </div>

        <div className="max-h-96 overflow-y-auto space-y-4 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <MessageCircle className="w-16 h-16 text-gray-500 mx-auto mb-4 opacity-50" />
              <p className="text-gray-400 text-lg">Start monitoring to see live sentiment analysis</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={message.id}
                className="flex items-start gap-4 p-4 bg-black/20 rounded-2xl border border-white/10 hover:bg-black/30 transition-all duration-300"
                style={{
                  animation: `slideInFromRight 0.5s ease-out ${index * 0.1}s both`
                }}
              >
                <div className="flex-shrink-0 mt-1">
                  {getEmotionIcon(message.emotion)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold text-white">{message.customer}</span>
                    <Badge className={`text-xs font-medium border ${getEmotionColor(message.emotion)}`}>
                      {message.emotion}
                    </Badge>
                    {message.emotion === "negative" && message.severity === "high" && (
                      <Badge className="bg-red-600/20 text-red-400 border-red-500/30 text-xs font-bold animate-pulse">
                        ALERT
                      </Badge>
                    )}
                  </div>
                  <p className="text-gray-300 leading-relaxed mb-2">{message.message}</p>
                  <p className="text-gray-500 text-xs">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(1deg); }
        }
        
        @keyframes slideInFromRight {
          0% {
            opacity: 0;
            transform: translateX(100px);
          }
          100% {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .custom-scrollbar {
          scrollbar-width: thin;
          scrollbar-color: rgba(147, 51, 234, 0.5) rgba(255, 255, 255, 0.1);
        }
        
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(147, 51, 234, 0.5);
          border-radius: 10px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(147, 51, 234, 0.7);
        }
      `}</style>
    </div>
  );
};

export default LiveSentimentDemo;