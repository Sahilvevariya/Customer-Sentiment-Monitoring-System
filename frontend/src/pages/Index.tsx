import React, { useState, useEffect } from 'react';
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plug, Brain, AlertTriangle, Heart, TrendingUp, Shield, Zap, ArrowRight, Star, Users, Clock, CheckCircle, Play, MessageCircle, BarChart3, Bell, Sparkles, Eye, Lightbulb, Target, Smile, Frown, Meh } from "lucide-react";

// Import the LiveSentimentDemo component
import LiveSentimentDemo from "@/components/LiveSentimentDemo";
import Navigation from "@/components/Navigation";

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

const Index = () => {
  const [activeDemo, setActiveDemo] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo(prev => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Brain,
      title: "AI Emotion Detection",
      description: "Advanced neural networks analyze tone, context, and emotional cues",
      gradient: "from-purple-500 to-pink-500",
      delay: 0
    },
    {
      icon: Bell,
      title: "Smart Alerts",
      description: "Intelligent notifications when sentiment drops below thresholds",
      gradient: "from-blue-500 to-cyan-500",
      delay: 0.2
    },
    {
      icon: BarChart3,
      title: "Trend Analysis",
      description: "Deep insights into customer satisfaction patterns over time",
      gradient: "from-green-500 to-emerald-500",
      delay: 0.4
    },
    {
      icon: Target,
      title: "Churn Prevention",
      description: "Proactive intervention before customers reach breaking point",
      gradient: "from-orange-500 to-red-500",
      delay: 0.6
    }
  ];

  const steps = [
    {
      number: "01",
      title: "Connect",
      subtitle: "Your Channels",
      description: "Seamlessly integrate with Zendesk, Slack, Intercom, and email in under 2 minutes",
      icon: Plug
    },
    {
      number: "02",
      title: "Analyze",
      subtitle: "Every Message",
      description: "AI processes conversations in real-time, detecting emotional patterns and urgency levels",
      icon: Eye
    },
    {
      number: "03",
      title: "Act",
      subtitle: "On Insights",
      description: "Get instant alerts and actionable recommendations to prevent churn",
      icon: Lightbulb
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-purple-900/20"></div>

        {/* Animated Orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-40 right-1/4 w-80 h-80 bg-gradient-to-r from-pink-600/20 to-purple-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-10 w-60 h-60 bg-gradient-to-r from-cyan-600/20 to-blue-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }}></div>

        {/* Grid Pattern */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)`,
          backgroundSize: '100px 100px'
        }}></div>
      </div>

      {/* Navigation */}
      <Navigation />

      {/* Hero Section */}
      <section className="relative z-10 px-6 pt-20 pb-32">
        <div className="max-w-7xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-sm border border-white/10 mb-8">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-white/90">AI-Powered Customer Intelligence</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black mb-8 leading-[0.9]">
            <span className="block text-white">Turn Customer</span>
            <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Frustration
            </span>
            <span className="block text-white">Into Loyalty</span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            Advanced AI monitors every customer interaction, predicting churn before it happens.
            <span className="text-purple-400 font-semibold"> Save customers you never knew you were losing.</span>
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <Link to="/start-monitoring">
              <Button className="group bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-10 py-4 text-lg font-bold rounded-2xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 hover:scale-105">
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button className="group bg-white/5 hover:bg-white/10 backdrop-blur-sm border border-white/20 text-white px-10 py-4 text-lg font-bold rounded-2xl transition-all duration-300 hover:scale-105">
              <Play className="mr-2 w-5 h-5 group-hover:scale-110 transition-transform" />
              Watch Demo
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {[
              { value: "94%", label: "Churn Reduction", icon: TrendingUp },
              { value: "2.3x", label: "Faster Resolution", icon: Clock },
              { value: "99.8%", label: "Accuracy Rate", icon: Target },
              { value: "24/7", label: "Monitoring", icon: Eye }
            ].map((stat, index) => (
              <FloatingCard key={index} delay={index * 0.2}>
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center hover:bg-white/10 transition-all duration-300">
                  <stat.icon className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-gray-400 text-sm">{stat.label}</div>
                </div>
              </FloatingCard>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Live Demo */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Experience Real-Time Analysis</h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">Watch our AI instantly detect customer emotions and prevent churn before it happens</p>
          </div>
          <LiveSentimentDemo />
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Powerful AI Features</h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">Advanced technology that understands your customers better than ever before</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <FloatingCard key={index} delay={feature.delay}>
                <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 rounded-3xl p-8 hover:from-white/15 hover:to-white/10 transition-all duration-500 group">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4 text-white">{feature.title}</h3>
                  <p className="text-gray-300 text-lg leading-relaxed">{feature.description}</p>
                </div>
              </FloatingCard>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">How It Works</h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">Three simple steps to transform your customer experience with AI</p>
          </div>

          <div className="relative">
            {/* Connection Line */}

            <div className="grid md:grid-cols-3 gap-12">
              {steps.map((step, index) => (
                <FloatingCard key={index} delay={index * 0.3}>
                  <div className="text-center group">
                    <div className="relative mb-8">
                      <div className="w-24 h-24 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                        <step.icon className="w-12 h-12 text-white" />
                      </div>
                      <div className="absolute -top-2 -right-2 w-12 h-12 bg-white rounded-full flex items-center justify-center text-black font-bold text-lg">
                        {step.number}
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold mb-2 text-white">{step.title}</h3>
                    <h4 className="text-lg text-purple-400 font-semibold mb-4">{step.subtitle}</h4>
                    <p className="text-gray-300 leading-relaxed">{step.description}</p>
                  </div>
                </FloatingCard>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <FloatingCard>
            <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-xl border border-white/20 rounded-3xl p-12">
              <Sparkles className="w-16 h-16 text-purple-400 mx-auto mb-6" />
              <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Prevent Churn?</h2>
              <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                Join 2,000+ companies using AI to keep their customers happy and loyal
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link to="/start-monitoring">
                  <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-12 py-4 text-xl font-bold rounded-2xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 hover:scale-105">
                    Start Free Trial
                    <ArrowRight className="ml-2 w-6 h-6" />
                  </Button>
                </Link>
                <p className="text-gray-400 text-sm">No credit card • 14-day free trial • Setup in 5 minutes</p>
              </div>
            </div>
          </FloatingCard>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-12 border-t border-white/10 mt-20">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-gray-500">© 2024 CustomerSentinel. All rights reserved.</p>
        </div>
      </footer>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(1deg); }
        }
      `}</style>
    </div>
  );
};

export default Index;