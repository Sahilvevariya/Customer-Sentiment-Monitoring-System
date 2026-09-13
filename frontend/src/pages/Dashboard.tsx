import { BarChart3, Bell, TrendingUp, Users, Activity, MessageCircle, Settings, Mail, Eye, Clock, AlertTriangle, CheckCircle, Zap } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import InteractiveEmotionChart from "@/components/InteractiveEmotionChart";
import { useState, useEffect } from "react";
import { SignedIn, SignedOut, RedirectToSignIn, useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
    const { user } = useUser();
    const userId = user?.id || 'default_user'; // Use real user ID or fallback to default

  const [emotionData, setEmotionData] = useState([
    { type: "Anger", count: 0, trend: "+0%", color: "emotion-negative" },
    { type: "Confusion", count: 0, trend: "+0%", color: "emotion-negative" },
    { type: "Joy", count: 0, trend: "+0%", color: "emotion-positive" },
    { type: "Neutral", count: 0, trend: "+0%", color: "emotion-neutral" },
  ]);

  const [recentTickets, setRecentTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [emailConfig, setEmailConfig] = useState(null);
  const navigate = useNavigate();

  // Fetch real emotion overview data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch emotion overview
        const emotionResponse = await fetch('https://customer-sentiment-te99.onrender.com/api/emotion-overview');
        if (emotionResponse.ok) {
          const emotionJson = await emotionResponse.json();

          const updatedEmotionData = [
            {
              type: "Anger",
              count: emotionJson.anger?.count || 0,
              trend: emotionJson.anger?.percentage_text || `${emotionJson.anger?.count || 0}/0 (0%)`,
              color: "emotion-negative"
            },
            {
              type: "Confusion",
              count: emotionJson.confusion?.count || 0,
              trend: emotionJson.confusion?.percentage_text || `${emotionJson.confusion?.count || 0}/0 (0%)`,
              color: "emotion-negative"
            },
            {
              type: "Joy",
              count: emotionJson.joy?.count || 0,
              trend: emotionJson.joy?.percentage_text || `${emotionJson.joy?.count || 0}/0 (0%)`,
              color: "emotion-positive"
            },
            {
              type: "Neutral",
              count: emotionJson.neutral?.count || 0,
              trend: emotionJson.neutral?.percentage_text || `${emotionJson.neutral?.count || 0}/0 (0%)`,
              color: "emotion-neutral"
            },
          ];
          setEmotionData(updatedEmotionData);
        }

        // Fetch recent negative sentiment messages for tickets
        const ticketsResponse = await fetch('https://customer-sentiment-te99.onrender.com/alerts?limit=3');
        if (ticketsResponse.ok) {
          const ticketsJson = await ticketsResponse.json();
          if (ticketsJson.messages && Array.isArray(ticketsJson.messages)) {
            const formattedTickets = ticketsJson.messages.map((msg: any, index: number) => ({
              id: `#${msg.id || (4521 - index)}`,
              customer: msg.sender || 'Unknown Customer',
              emotion: (msg.sentiment || msg.emotion || 'unknown').charAt(0).toUpperCase() + (msg.sentiment || msg.emotion || 'unknown').slice(1),
              severity: msg.sentiment === 'angry' ? 'High' : msg.sentiment === 'confused' ? 'Medium' : 'Low',
              time: msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : 'Unknown'
            }));
            setRecentTickets(formattedTickets);
          }
        }

        // Fetch email configuration
        const configResponse = await fetch(`https://customer-sentiment-te99.onrender.com/api/email-config?user_id=${userId}`);
        if (configResponse.ok) {
          const configJson = await configResponse.json();
          setEmailConfig(configJson);
        }

        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh data every 30 seconds for more frequent updates
    const interval = setInterval(fetchDashboardData, 30000);

    return () => clearInterval(interval);
  }, [userId]);

  return (
    <>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <div className="min-h-screen bg-gray-900">
          {/* Header */}
          <header className="bg-gray-800 border-b border-gray-700">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">

                  <div>
                    <h1 className="text-xl font-bold text-white">CustomerSentinel</h1>

                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {emailConfig && (
                    <div className="flex items-center space-x-2 px-4 py-2 bg-gray-700 rounded-lg">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-300 text-sm">{emailConfig.email}</span>
                    </div>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate('/start-monitoring')}
                    className="border-gray-600 text-gray-300 hover:bg-gray-700"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </Button>
                </div>
              </div>
            </div>
          </header>

          <div className="container mx-auto px-6 py-8">
            {/* Welcome Section */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">Welcome back!</h2>
              <p className="text-gray-400">Here's what's happening with your customer sentiment today.</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                      <AlertTriangle className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-gray-500 text-sm">Today</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {loading ? "..." : emotionData.find(e => e.type === "Anger")?.count || 0}
                  </div>
                  <div className="text-gray-400 text-sm">Angry Customers</div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                      <MessageCircle className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-gray-500 text-sm">Today</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {loading ? "..." : emotionData.find(e => e.type === "Confusion")?.count || 0}
                  </div>
                  <div className="text-gray-400 text-sm">Confused Customers</div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-gray-500 text-sm">Today</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {loading ? "..." : emotionData.find(e => e.type === "Joy")?.count || 0}
                  </div>
                  <div className="text-gray-400 text-sm">Happy Customers</div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-gray-500 text-sm">Today</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">
                    {loading ? "..." : emotionData.find(e => e.type === "Neutral")?.count || 0}
                  </div>
                  <div className="text-gray-400 text-sm">Neutral Interactions</div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Emotion Chart */}
              <div className="lg:col-span-2">
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-2xl font-bold text-white">Sentiment Trends</CardTitle>
                    <CardDescription className="text-gray-400">
                      Real-time emotion analysis across all channels
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span className="text-gray-400 text-sm">Anger</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span className="text-gray-400 text-sm">Confusion</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="text-gray-400 text-sm">Joy</span>
                        </div>
                      </div>
                    </div>
                    <InteractiveEmotionChart />
                  </CardContent>
                </Card>
              </div>

              {/* Recent Alerts */}
              <div className="lg:col-span-1 space-y-6">
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl font-bold text-white">Recent Alerts</CardTitle>
                      <Bell className="w-5 h-5 text-gray-400" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                          <div key={i} className="animate-pulse">
                            <div className="h-16 bg-gray-700 rounded-lg"></div>
                          </div>
                        ))}
                      </div>
                    ) : recentTickets.length > 0 ? (
                      <div className="space-y-4">
                        {recentTickets.map((ticket: any, index: number) => (
                          <div key={index} className="bg-gray-700 rounded-xl p-4 border border-gray-600 hover:bg-gray-700/80 transition-colors">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  ticket.severity === 'High' ? 'bg-red-500' : 
                                  ticket.severity === 'Medium' ? 'bg-yellow-500' : 'bg-blue-500'
                                }`}></div>
                                <span className="text-white font-medium text-sm">{ticket.id}</span>
                              </div>
                              <span className="text-gray-500 text-xs">{ticket.time}</span>
                            </div>
                            <div className="text-white text-sm mb-1">{ticket.customer}</div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400 text-xs">{ticket.emotion}</span>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                ticket.severity === 'High' ? 'bg-red-500/20 text-red-300' : 
                                ticket.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-blue-500/20 text-blue-300'
                              }`}>
                                {ticket.severity}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                          <CheckCircle className="w-8 h-8 text-gray-500" />
                        </div>
                        <p className="text-gray-400 text-sm">No alerts right now</p>
                        <p className="text-gray-500 text-xs">All customers are happy!</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-xl font-bold text-white">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                      onClick={() => navigate('/start-monitoring')}
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Start Monitoring
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full border-gray-600 text-gray-300 hover:bg-gray-700"
                      onClick={() => navigate('/gmail-setup')}
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Configure Email
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>

            {error && (
              <div className="mt-8 p-4 bg-red-500/20 border border-red-500/30 text-red-300 rounded-xl">
                {error}
              </div>
            )}
          </div>
        </div>
      </SignedIn>
    </>
  );
};

export default Dashboard;