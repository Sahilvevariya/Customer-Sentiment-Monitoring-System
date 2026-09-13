import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Dashboard from "./pages/Dashboard";
import StartMonitoring from "./pages/StartMonitoring";
import ScheduleDemo from "./pages/ScheduleDemo";
import NotFound from "./pages/NotFound";
import GmailSetup from "@/pages/GmailSetup";
import EmailConfigTest from "@/components/EmailConfigTest";
import Chat from "@/pages/Chat";
import SentimentDashboard from "@/pages/SentimentDashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chatdashboard" element={<SentimentDashboard />} />
          <Route path="/start-monitoring" element={<StartMonitoring />} />
          <Route path="/schedule-demo" element={<ScheduleDemo />} />
          <Route path="/gmail-setup" element={<GmailSetup />} />
          <Route path="/test-email" element={<EmailConfigTest />} />
          <Route path="/chat" element={<Chat />} />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
