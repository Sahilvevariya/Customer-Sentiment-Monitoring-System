import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Eye, EyeOff, Mail, MessageSquare, Shield, InfoIcon, CheckCircle2, KeyRound, Bot } from "lucide-react";
import { useUser } from "@clerk/clerk-react";

interface EmailConfig {
  email: string;
  appPassword: string;
  telegramUserId: string;
}

interface EmailMonitoringSetupProps {
  onConfigSaved: (config: EmailConfig) => void;
  existingConfig?: EmailConfig | null;
}

const EmailMonitoringSetup = ({ onConfigSaved, existingConfig }: EmailMonitoringSetupProps) => {
  const { user } = useUser();
  const userId = user?.id || 'default_user';

  const [config, setConfig] = useState<EmailConfig>({
    email: existingConfig?.email || '',
    appPassword: existingConfig?.appPassword || '',
    telegramUserId: existingConfig?.telegramUserId || ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleInputChange = (field: keyof EmailConfig, value: string) => {
    setConfig(prev => ({ ...prev, [field]: value }));
    setError(null);
    setSuccess(false);
  };

  const validateConfig = () => {
    if (!config.email.trim()) {
      setError("Email address is required");
      return false;
    }
    if (!config.email.includes('@')) {
      setError("Please enter a valid email address");
      return false;
    }
    if (!config.appPassword.trim()) {
      setError("App password is required");
      return false;
    }
    if (config.appPassword.length < 4) {
      setError("App password must be at least 4 characters long");
      return false;
    }
    if (!config.telegramUserId.trim()) {
      setError("Telegram User ID is required");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log("Form submitted with config:", config);

    if (!validateConfig()) {
      console.log("Validation failed");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log("Sending request to backend...");

      const response = await fetch('https://customer-sentiment-te99.onrender.com/api/email-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...config,
          user_id: userId
        }),
      });

      console.log("Response received:", response.status);

      if (!response.ok) {
        const errorData = await response.text();
        console.error("Response error:", errorData);
        throw new Error(`Failed to save email configuration: ${response.status}`);
      }

      const result = await response.json();
      console.log("Success result:", result);

      if (result.data_reset) {
        console.log("✅ Data was automatically reset due to new email/password configuration");
      }

      setSuccess(true);
      onConfigSaved(config);

    } catch (err) {
      console.error("Error saving config:", err);
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full bg-gray-800 border border-gray-700 rounded-xl p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {success && (
          <Alert className="bg-green-900/30 border-green-800 text-green-300">
            <CheckCircle2 className="h-5 w-5 text-green-400" />
            <AlertDescription className="text-green-400">
              Configuration saved successfully! Data has been reset to start from zero.
              Your email monitoring is now ready to begin fresh tracking.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="bg-red-900/30 border-red-800 text-red-300">
            <InfoIcon className="h-5 w-5 text-red-400" />
            <AlertDescription className="text-red-400">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Email Address */}
        <div className="space-y-3">
          <Label htmlFor="email" className="text-gray-300 text-sm font-medium flex items-center gap-2">
            <Mail className="h-4 w-4 text-blue-400" />
            Gmail Address
          </Label>
          <Input
            id="email"
            type="email"
            placeholder="your.email@gmail.com"
            value={config.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            className="bg-gray-700 border-gray-600 focus:border-blue-400 text-white placeholder-gray-500"
            required
          />
          <p className="text-xs text-gray-500">
            The Gmail account you want to monitor for customer emails
          </p>
        </div>

        {/* App Password */}
        <div className="space-y-3">
          <Label htmlFor="appPassword" className="text-gray-300 text-sm font-medium flex items-center gap-2">
            <KeyRound className="h-4 w-4 text-blue-400" />
            Gmail App Password
          </Label>
          <div className="relative">
            <Input
              id="appPassword"
              type={showPassword ? "text" : "password"}
              placeholder="xxxx xxxx xxxx xxxx"
              value={config.appPassword}
              onChange={(e) => handleInputChange('appPassword', e.target.value)}
              className="bg-gray-700 border-gray-600 focus:border-blue-400 text-white placeholder-gray-500 pr-12"
              required
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 hover:bg-gray-600"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="text-xs text-gray-500 space-y-1">
            <p>• Generate an App Password from your Google Account settings</p>
            <p>• Go to Account → Security → 2-Step Verification → App passwords</p>
            <p>• Select "Mail" and your device to generate the password</p>
          </div>
        </div>

        {/* Telegram User ID */}
        <div className="space-y-3">
          <Label htmlFor="telegramUserId" className="text-gray-300 text-sm font-medium flex items-center gap-2">
            <Bot className="h-4 w-4 text-blue-400" />
            Telegram User ID
          </Label>
          <Input
            id="telegramUserId"
            type="text"
            placeholder="123456789"
            value={config.telegramUserId}
            onChange={(e) => handleInputChange('telegramUserId', e.target.value)}
            className="bg-gray-700 border-gray-600 focus:border-blue-400 text-white placeholder-gray-500"
            required
          />
          <div className="text-xs text-gray-500 space-y-1">
            <p>• Message @userinfobot on Telegram to get your User ID</p>
            <p>• Used for sending real-time sentiment alerts</p>
          </div>
        </div>


        {/* Submit Button */}
        <div className="pt-2">
          <Button
            type="submit"
            className="w-full h-12 font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white transition-all duration-200"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Saving Configuration...
              </>
            ) : (
              <>
                <MessageSquare className="mr-2 h-5 w-5" />
                Save & Start Monitoring
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default EmailMonitoringSetup;