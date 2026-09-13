import { useState } from "react";
import { Calendar, Clock, User, Video } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const ScheduleDemo = () => {
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const timeSlots = [
    "9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"
  ];

  const features = [
    "Real-time emotion detection demo",
    "Live sentiment analysis walkthrough", 
    "Integration setup guidance",
    "Custom alert configuration",
    "ROI and pricing discussion"
  ];

  return (
    <div className="min-h-screen bg-gradient-hero waveform p-6">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            Schedule a Live Demo
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Need a walkthrough? Schedule a 15-min live demo with our team and see CustomerSentinel in action.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Demo Details */}
          <Card className="bg-gradient-card border-border glow-primary">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground">
                <Video size={24} className="text-primary" />
                <span>What You'll See</span>
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                A comprehensive walkthrough of CustomerSentinel's AI-powered emotion detection
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <ul className="space-y-3">
                {features.map((feature, index) => (
                  <li key={index} className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <span className="text-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <div className="mt-6 p-4 bg-muted/10 rounded-lg">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                  <Clock size={16} />
                  <span>Duration: 15 minutes</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <User size={16} />
                  <span>1-on-1 with our product specialist</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Calendar Booking */}
          <Card className="bg-gradient-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground">
                <Calendar size={24} className="text-primary" />
                <span>Choose Your Time</span>
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Select a convenient time slot for your personalized demo
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {/* Mock Calendar Interface */}
              <div className="space-y-4">
                <div className="text-center p-4 bg-muted/10 rounded-lg">
                  <h3 className="font-medium text-foreground mb-2">Tomorrow, January 20th</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {timeSlots.map((time) => (
                      <Button
                        key={time}
                        variant={selectedTime === time ? "default" : "outline"}
                        className={selectedTime === time ? "cta-button" : "border-border hover:border-primary"}
                        size="sm"
                        onClick={() => setSelectedTime(time)}
                      >
                        {time}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="text-center p-4 bg-muted/10 rounded-lg">
                  <h3 className="font-medium text-foreground mb-2">Wednesday, January 21st</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {timeSlots.slice(0, 4).map((time) => (
                      <Button
                        key={`wed-${time}`}
                        variant={selectedTime === `wed-${time}` ? "default" : "outline"}
                        className={selectedTime === `wed-${time}` ? "cta-button" : "border-border hover:border-primary"}
                        size="sm"
                        onClick={() => setSelectedTime(`wed-${time}`)}
                      >
                        {time}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Calendly Integration Placeholder */}
                <div className="mt-6 p-6 bg-primary/5 border border-primary/20 rounded-lg text-center">
                  <p className="text-muted-foreground text-sm mb-4">
                    Integrated calendar booking system
                  </p>
                  <Button 
                    className="cta-button" 
                    disabled={!selectedTime}
                  >
                    {selectedTime ? 'Book Selected Time' : 'Select a Time Slot'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 text-center">
          <p className="text-muted-foreground mb-4">
            Trusted by CX teams at leading companies
          </p>
          <div className="flex justify-center space-x-8 opacity-60">
            <div className="w-24 h-8 bg-muted/20 rounded flex items-center justify-center text-xs">
              Company A
            </div>
            <div className="w-24 h-8 bg-muted/20 rounded flex items-center justify-center text-xs">
              Company B
            </div>
            <div className="w-24 h-8 bg-muted/20 rounded flex items-center justify-center text-xs">
              Company C
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScheduleDemo;