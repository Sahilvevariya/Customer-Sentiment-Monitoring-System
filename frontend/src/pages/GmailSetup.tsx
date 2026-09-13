import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { SignedIn, SignedOut, RedirectToSignIn, useUser } from "@clerk/clerk-react";
import EmailMonitoringSetup from "../components/EmailMonitoringSetup";
import { ArrowLeft, Mail, Shield, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

const GmailSetup = () => {
  const { user } = useUser();
  const userId = user?.id || 'default_user'; // Use real user ID or fallback to default

  const [existingConfig, setExistingConfig] = useState(null);
  const navigate = useNavigate();

  // Check if email is already configured
  useEffect(() => {
    const checkEmailConfig = async () => {
      try {
        const response = await fetch(`https://customer-sentiment-te99.onrender.com/api/email-config?user_id=${userId}`);
        if (response.ok) {
          const config = await response.json();
          setExistingConfig(config);
        }
      } catch (error) {
        console.error('Failed to fetch email config:', error);
      }
    };

    checkEmailConfig();
  }, [userId]);

  const handleConfigSaved = (config: any) => {
    console.log("Email configuration saved:", config);
    // Redirect to dashboard after successful configuration
    navigate("/dashboard");
  };

  return (
    <>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
      <SignedIn>
        <div className="min-h-screen bg-gray-900 text-white font-sans flex flex-col items-center justify-center p-6">
          <div className="w-full max-w-2xl bg-gray-800 p-8 rounded-2xl shadow-lg border border-gray-700">
            {/* Back Button */}
            <div className="mb-6">
              <Button
                variant="outline"
                onClick={() => navigate("/start-monitoring")}
                className="flex items-center space-x-2 bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600"
              >
                <ArrowLeft size={16} />
                <span>Back to Setup</span>
              </Button>
            </div>

            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 flex items-center justify-center mx-auto mb-4 bg-gradient-to-br from-red-500 to-pink-600 rounded-full shadow-lg">
                <Mail className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Gmail Monitoring Setup
              </h1>
              <p className="text-lg text-gray-400">
                Connect your Gmail account to start monitoring customer sentiment in real-time.
              </p>
            </div>

            {/* Email Configuration Component */}
            <EmailMonitoringSetup
              onConfigSaved={handleConfigSaved}
              existingConfig={existingConfig}
            />

            {/* Background Visualization & Secure Message */}
            <div className="mt-8 text-center">
              <div className="w-full p-4 bg-gray-700 rounded-xl flex items-center justify-center space-x-2 border border-gray-600">
                <Shield className="w-5 h-5 text-green-400" />
                <p className="text-gray-300 text-sm">Your connection is secure and encrypted.</p>
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
    </>
  );
};

export default GmailSetup;
