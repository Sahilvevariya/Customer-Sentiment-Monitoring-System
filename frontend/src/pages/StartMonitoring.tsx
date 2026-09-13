import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Mail, MessageSquare,ArrowLeftRight, Slack, Zap, Settings, CheckCircle, ArrowRight, Shield, Bell, TrendingUp, Users, Target, Play, Sparkles } from "lucide-react";
import { SignedIn, SignedOut, RedirectToSignIn, useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";

const StartMonitoring = () => {
  const { user } = useUser();
  const userId = user?.id || 'default_user'; // Use real user ID or fallback to default
  
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [alertThreshold, setAlertThreshold] = useState("");
  const [notificationChannel, setNotificationChannel] = useState("");
  const [emailConfigured, setEmailConfigured] = useState(false);
  const [existingEmailConfig, setExistingEmailConfig] = useState(null);
  const [advancedSettings, setAdvancedSettings] = useState({
    realTimeMonitoring: true,
    weekendAlerts: false,
    escalationEnabled: true,
    customKeywords: false
  });

  const navigate = useNavigate();

  // Check if email is already configured
  useEffect(() => {
    const checkEmailConfig = async () => {
      try {
        const response = await fetch(`https://customer-sentiment-te99.onrender.com/api/email-config?user_id=${userId}`);
        if (response.ok) {
          const config = await response.json();
          setExistingEmailConfig(config);
          setEmailConfigured(true);
          if (config.email) {
            setSelectedPlatforms(prev => prev.includes("gmail") ? prev : [...prev, "gmail"]);
          }
        }
      } catch (error) {
        console.error('Failed to fetch email config:', error);
      }
    };

    checkEmailConfig();
  }, [userId]);

  const platforms = [
    { id: "gmail", name: "Gmail", icon: Mail, description: "Connect your Gmail support inbox", color: "from-red-500 to-pink-600" },
    { id: "Drift", name: "Drift", icon: MessageSquare, description: "Monitor realtime conversationHea", color: "from-orange-500 to-purple-600" },
    { id: "zendesk", name: "Zendesk", icon:ArrowLeftRight, description: "Analyze Zendesk support tickets", color: "from-yellow-500 to-emerald-600" },
  ];

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handlePlatformClick = (platformId: string) => {
    if (platformId === "gmail") {
      // Always navigate to Gmail setup page when Gmail is clicked
      navigate("/gmail-setup");
    }if (platformId === "Drift") {
      // Always navigate to Gmail setup page when Gmail is clicked
      navigate("/chatdashboard");
    }if (platformId === "zendesk") {
      // Always navigate to Gmail setup page when Gmail is clicked
      navigate("/chatdashboard");
    } else {
      handlePlatformToggle(platformId);
    }
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedPlatforms.length === 0) {
      return;
    }

    try {
      // If Gmail is selected and configured, start monitoring
      if (selectedPlatforms.includes("gmail") && emailConfigured) {
        const response = await fetch('https://customer-sentiment-te99.onrender.com/api/start-live-monitoring', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
            user_id: userId,
            reset_data: true
          }),
        });

        if (response.ok) {
          const result = await response.json();
          console.log("Monitoring started:", result);

          // Navigate to dashboard
          navigate("/dashboard");
        } else {
          console.error("Failed to start monitoring");
        }
      } else {
        console.log("Starting monitoring with:", {
          platforms: selectedPlatforms,
          threshold: alertThreshold,
          notifications: notificationChannel
        });

        // Navigate to dashboard anyway for other platforms
        navigate("/dashboard");
      }
    } catch (error) {
      console.error("Error starting monitoring:", error);
    }
  };

  return (
    <>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <div className="min-h-screen bg-gray-900 text-white font-sans">
          {/* Header */}
          <header className="sticky top-0 z-50 bg-gray-900/90 backdrop-blur-md border-b border-gray-800">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <h1 className="text-xl font-bold text-white">CustomerSentinel</h1>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/')}
                  className="bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Back to Home
                </Button>
              </div>
            </div>
          </header>

          <div className="container mx-auto px-6 py-16">
            {/* Hero Section */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 mb-6">
                <Sparkles className="w-4 h-4 mr-2" />
                <span className="text-sm font-medium">Setup Monitoring</span>
              </div>

              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Start Monitoring Your
                <span className="block text-blue-400">
                  Customer Sentiment
                </span>
              </h1>

              <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                Connect your support channels and set up AI-powered emotion detection to prevent customer churn before it happens.
              </p>
            </div>

            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSubmit} className="space-y-12">
                {/* Platform Selection */}
                <div className="bg-gray-800 p-8 rounded-2xl shadow-lg border border-gray-700">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-white mb-2">Connect Your Support Channels</h2>
                    <p className="text-gray-400">Choose which platforms you'd like CustomerSentinel to monitor.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {platforms.map((platform) => (
                      <div
                        key={platform.id}
                        className={`relative group cursor-pointer transition-all duration-300 p-6 rounded-xl border-2 ${
                          selectedPlatforms.includes(platform.id)
                            ? "border-blue-500 bg-gray-700 shadow-xl"
                            : "border-gray-700 bg-gray-800 hover:bg-gray-700"
                        }`}
                        onClick={() => handlePlatformClick(platform.id)}
                      >
                        <div className="flex items-center space-x-4">
                          <div className={`w-12 h-12 flex items-center justify-center rounded-full bg-gradient-to-r ${platform.color}`}>
                            <platform.icon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="text-lg font-semibold text-white">{platform.name}</h3>
                              {platform.id === "gmail" && emailConfigured && (
                                <div className="flex items-center px-2 py-1 bg-green-500/20 rounded-full">
                                  <CheckCircle className="w-3 h-3 text-green-400" />
                                  <span className="text-green-400 text-xs font-medium">Connected</span>
                                </div>
                              )}
                            </div>
                            <p className="text-sm text-gray-400">{platform.description}</p>
                            {platform.id === "gmail" && !emailConfigured && (
                              <p className="text-orange-400 text-xs font-medium mt-1">
                                ⚠️ Requires configuration
                              </p>
                            )}
                          </div>
                          <Checkbox
                            checked={selectedPlatforms.includes(platform.id)}
                            onChange={() => handlePlatformToggle(platform.id)}
                            className="w-5 h-5"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Alert Settings */}
                <div className="bg-gray-800 p-8 rounded-2xl shadow-lg border border-gray-700">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-white mb-2">Alert Configuration</h2>
                    <p className="text-gray-400">Control how and when you receive sentiment alerts.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                      <div>
                        <Label className="text-gray-300 font-medium mb-2 block">Alert Threshold</Label>
                        <Select value={alertThreshold} onValueChange={setAlertThreshold}>
                          <SelectTrigger className="bg-gray-700 border-gray-600 text-white rounded-lg">
                            <SelectValue placeholder="Select threshold" />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-800 border-gray-700 text-white">
                            <SelectItem value="low">Low - Any negative sentiment</SelectItem>
                            <SelectItem value="medium">Medium - Moderate frustration</SelectItem>
                            <SelectItem value="high">High - Severe anger/confusion</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label className="text-gray-300 font-medium mb-2 block">Notification Channel</Label>
                        <Select value={notificationChannel} onValueChange={setNotificationChannel}>
                          <SelectTrigger className="bg-gray-700 border-gray-600 text-white rounded-lg">
                            <SelectValue placeholder="Select channel" />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-800 border-gray-700 text-white">
                            <SelectItem value="email">Email</SelectItem>
                            <SelectItem value="telegram">Telegram</SelectItem>
                            <SelectItem value="webhook">Webhook</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-gray-700 rounded-xl">
                        <div>
                          <div className="text-white font-medium">Real-time Monitoring</div>
                          <div className="text-gray-400 text-sm">Monitor sentiment continuously</div>
                        </div>
                        <Switch
                          checked={advancedSettings.realTimeMonitoring}
                          onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, realTimeMonitoring: checked }))}
                        />
                      </div>

                      <div className="flex items-center justify-between p-4 bg-gray-700 rounded-xl">
                        <div>
                          <div className="text-white font-medium">Weekend Alerts</div>
                          <div className="text-gray-400 text-sm">Receive alerts on weekends</div>
                        </div>
                        <Switch
                          checked={advancedSettings.weekendAlerts}
                          onCheckedChange={(checked) => setAdvancedSettings(prev => ({ ...prev, weekendAlerts: checked }))}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Start Monitoring Button */}
                <div className="text-center mt-12">
                  <Button
                    type="submit"
                    className="group bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-12 py-4 text-xl font-semibold rounded-full shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 hover:scale-105"
                    disabled={selectedPlatforms.length === 0}
                  >
                    <Zap className="w-6 h-6 mr-3" />
                    Start Monitoring
                    <ArrowRight className="w-6 h-6 ml-3 group-hover:translate-x-1 transition-transform" />
                  </Button>

                  {selectedPlatforms.length === 0 && (
                    <p className="text-gray-500 text-sm mt-4">Please select at least one platform to continue</p>
                  )}
                </div>
              </form>
            </div>
          </div>

          {/* Footer */}
          <footer className="relative z-10 px-6 py-12 border-t border-gray-800">
            <div className="max-w-6xl mx-auto text-center">
              <p className="text-gray-500">© 2024 CustomerSentinel. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </SignedIn>
    </>
  );
};

export default StartMonitoring;
