import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Mail, MessageSquare, Headphones, Slack, Zap, Settings, CheckCircle } from "lucide-react";
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
    { id: "gmail", name: "Gmail", icon: Mail, description: "Connect your Gmail support inbox" },
    { id: "intercom", name: "Intercom", icon: MessageSquare, description: "Monitor Intercom conversations" },
    { id: "zendesk", name: "Zendesk", icon: Headphones, description: "Analyze Zendesk support tickets" },
    { id: "slack", name: "Slack", icon: Slack, description: "Track customer messages in Slack" },
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
        <div className="min-h-screen bg-gradient-hero waveform p-6">
          <div className="container mx-auto max-w-4xl">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-foreground mb-4">
                Start Monitoring Customer Sentiment
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Connect your support channels and set up AI-powered emotion detection to prevent customer churn before it happens.
              </p>
            </div>

            <Card className="bg-gradient-card border-border glow-primary">
              <CardHeader>
                <CardTitle className="text-2xl font-semibold text-foreground">
                  Connect Your Support Channels
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Choose which platforms you'd like CustomerSentinel to monitor for emotional sentiment
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-8">
                  {/* Platform Selection */}
                  <div className="space-y-4">
                    <Label className="text-lg font-medium text-foreground">
                      Select Platforms to Monitor
                    </Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {platforms.map((platform) => (
                        <div
                          key={platform.id}
                          className={`p-4 rounded-lg border cursor-pointer transition-all duration-300 ${
                            selectedPlatforms.includes(platform.id)
                              ? "border-primary bg-primary/10 glow-primary"
                              : "border-border bg-muted/10 hover:border-primary/50"
                          }`}
                          onClick={() => handlePlatformClick(platform.id)}
                        >
                          <div className="flex items-center space-x-3">
                            <Checkbox
                              checked={selectedPlatforms.includes(platform.id)}
                              onChange={() => handlePlatformToggle(platform.id)}
                            />
                            <platform.icon size={24} className="text-primary" />
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <h3 className="font-medium text-foreground">{platform.name}</h3>
                                {platform.id === "gmail" && emailConfigured && (
                                  <CheckCircle size={16} className="text-green-500" />
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {platform.description}
                                {platform.id === "gmail" && emailConfigured && existingEmailConfig && (
                                  <span className="text-green-600 block">
                                    ✓ Configured: {(existingEmailConfig as any).email}
                                  </span>
                                )}
                                {platform.id === "gmail" && !emailConfigured && (
                                  <span className="text-orange-600 block">
                                    Click to configure Gmail monitoring
                                  </span>
                                )}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Alert Preferences */}
                  <div className="space-y-4">
                    <Label className="text-lg font-medium text-foreground">
                      Alert Sensitivity
                    </Label>
                    <Select value={alertThreshold} onValueChange={setAlertThreshold}>
                      <SelectTrigger className="bg-input border-border">
                        <SelectValue placeholder="Choose when to receive alerts" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">High Sensitivity - Alert on any negative sentiment</SelectItem>
                        <SelectItem value="medium">Medium Sensitivity - Alert on moderate to high negativity</SelectItem>
                        <SelectItem value="low">Low Sensitivity - Alert only on severe negativity</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Notification Channel */}
                  <div className="space-y-4">
                    <Label className="text-lg font-medium text-foreground">
                      How should we notify you?
                    </Label>
                    <Select value={notificationChannel} onValueChange={setNotificationChannel}>
                      <SelectTrigger className="bg-input border-border">
                        <SelectValue placeholder="Select notification method" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="email">📧 Email notifications</SelectItem>
                        <SelectItem value="slack">💬 Slack integration</SelectItem>
                        <SelectItem value="webhook">🔗 Webhook (custom integration)</SelectItem>
                        <SelectItem value="dashboard">📊 Dashboard only</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Advanced Settings */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Settings className="w-5 h-5 text-primary" />
                      <Label className="text-lg font-medium text-foreground">
                        Advanced Settings
                      </Label>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-muted/10 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-sm font-medium text-foreground">Real-time Monitoring</Label>
                          <p className="text-xs text-muted-foreground">Monitor conversations as they happen</p>
                        </div>
                        <Switch
                          checked={advancedSettings.realTimeMonitoring}
                          onCheckedChange={(checked) => 
                            setAdvancedSettings(prev => ({ ...prev, realTimeMonitoring: checked }))
                          }
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-sm font-medium text-foreground">Weekend Alerts</Label>
                          <p className="text-xs text-muted-foreground">Receive alerts during weekends</p>
                        </div>
                        <Switch
                          checked={advancedSettings.weekendAlerts}
                          onCheckedChange={(checked) => 
                            setAdvancedSettings(prev => ({ ...prev, weekendAlerts: checked }))
                          }
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-sm font-medium text-foreground">Auto Escalation</Label>
                          <p className="text-xs text-muted-foreground">Automatically escalate urgent issues</p>
                        </div>
                        <Switch
                          checked={advancedSettings.escalationEnabled}
                          onCheckedChange={(checked) => 
                            setAdvancedSettings(prev => ({ ...prev, escalationEnabled: checked }))
                          }
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-sm font-medium text-foreground">Custom Keywords</Label>
                          <p className="text-xs text-muted-foreground">Monitor specific words or phrases</p>
                        </div>
                        <Switch
                          checked={advancedSettings.customKeywords}
                          onCheckedChange={(checked) => 
                            setAdvancedSettings(prev => ({ ...prev, customKeywords: checked }))
                          }
                        />
                      </div>
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-6">
                    <Button 
                      type="submit" 
                      className="w-full cta-button text-lg py-6"
                      disabled={selectedPlatforms.length === 0}
                    >
                      <Zap className="mr-2" size={20} />
                      Start Listening Now
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Background Visualization */}
            <div className="mt-12 text-center">
              <div className="w-full h-32 bg-gradient-accent/10 rounded-xl flex items-center justify-center waveform">
                <p className="text-muted-foreground">Dynamic emotional signal visualizer</p>
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
    </>
  );
};

export default StartMonitoring;
