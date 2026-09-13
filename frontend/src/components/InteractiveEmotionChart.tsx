import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, Play, Pause, RotateCcw } from "lucide-react";
import { useUser } from "@clerk/clerk-react";

interface EmotionDataPoint {
  time: string;
  positive: number;
  negative: number;
  neutral: number;
  alerts: number;
}

const InteractiveEmotionChart = () => {
  const { user } = useUser();
  const userId = user?.id || 'default_user';

  const [data, setData] = useState<EmotionDataPoint[]>([
    { time: '09:00', positive: 65, negative: 20, neutral: 15, alerts: 2 },
    { time: '10:00', positive: 70, negative: 18, neutral: 12, alerts: 1 },
    { time: '11:00', positive: 60, negative: 25, neutral: 15, alerts: 3 },
    { time: '12:00', positive: 55, negative: 30, neutral: 15, alerts: 4 },
    { time: '13:00', positive: 75, negative: 15, neutral: 10, alerts: 1 },
    { time: '14:00', positive: 80, negative: 10, neutral: 10, alerts: 0 },
  ]);

  const [isLive, setIsLive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLiveMonitoring, setIsLiveMonitoring] = useState(false);

  // Live button now automatically starts email monitoring and resets data
  const startLiveMonitoring = async () => {
    try {
      setError(null);
      console.log('🔄 Starting live monitoring with fresh data...');

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
        console.log('✅ Live monitoring started successfully!', result);
        setIsLiveMonitoring(true);

        // Clear current data to show fresh start
        setData([]);

        if (result.data_reset) {
          console.log('📊 Data reset to zero - monitoring will show fresh results');
        }
      } else {
        const errorData = await response.text();
        throw new Error(`Failed to start monitoring: ${errorData}`);
      }
    } catch (error) {
      console.error('❌ Failed to start live monitoring:', error);
      setError('Failed to start live monitoring. Please check your email configuration.');
    }
  };

  // Function to fetch real emotion trends data from backend
  const fetchEmotionTrends = async () => {
    try {
      const response = await fetch('https://customer-sentiment-te99.onrender.com/api/emotion-trends');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const json = await response.json();

      if (json.trends) {
        // Transform backend data to chart format
        const chartData: EmotionDataPoint[] = [];

        if (Array.isArray(json.trends)) {
          json.trends.forEach((trend: any) => {
            const total = (trend.joy || 0) + (trend.anger || 0) + (trend.confusion || 0) + (trend.neutral || 0);
            const positive = total > 0 ? Math.round(((trend.joy || 0) / total) * 100) : 0;
            const negative = total > 0 ? Math.round(((trend.anger || 0) + (trend.confusion || 0)) / total * 100) : 0;
            const neutral = total > 0 ? Math.round(((trend.neutral || 0) / total) * 100) : 0;

            chartData.push({
              time: trend.time,
              positive,
              negative: negative,
              neutral,
              alerts: trend.anger || 0
            });
          });
        }

        // Sort by time and take last 12 hours
        chartData.sort((a, b) => a.time.localeCompare(b.time));
        setData(chartData.length > 0 ? chartData.slice(-6) : chartData);
        setError(null);
      } else {
        throw new Error('No trends data received from backend');
      }
    } catch (error) {
      console.error('Failed to fetch emotion trends:', error);
      // Use sample data if API fails
      setData([
        { time: '09:00', positive: 65, negative: 20, neutral: 15, alerts: 2 },
        { time: '10:00', positive: 70, negative: 18, neutral: 12, alerts: 1 },
        { time: '11:00', positive: 60, negative: 25, neutral: 15, alerts: 3 },
        { time: '12:00', positive: 55, negative: 30, neutral: 15, alerts: 4 },
        { time: '13:00', positive: 75, negative: 15, neutral: 10, alerts: 1 },
        { time: '14:00', positive: 80, negative: 10, neutral: 10, alerts: 0 },
      ]);
    }
  };

  // Fetch real data from backend on mount
  useEffect(() => {
    fetchEmotionTrends();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isLive) {
      if (!isLiveMonitoring) {
        startLiveMonitoring();
      }

      interval = setInterval(() => {
        fetchEmotionTrends();
      }, 10000);
    } else {
      setIsLiveMonitoring(false);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLive, isLiveMonitoring]);

  const resetData = async () => {
    try {
      setIsLive(false);
      setIsLiveMonitoring(false);
      setError(null);

      console.log('🔄 Resetting all emotion data...');

      const response = await fetch('https://customer-sentiment-te99.onrender.com/api/reset-emotion-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Data reset successfully:', result);

        setData([]);
        fetchEmotionTrends();
      } else {
        throw new Error('Failed to reset data');
      }
    } catch (error) {
      console.error('❌ Failed to reset data:', error);
      setError('Failed to reset data. Please try again.');
      fetchEmotionTrends();
    }
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum: number, entry: any) => sum + entry.value, 0);

      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-xl">
          <p className="text-white font-bold text-sm mb-2">{`Time: ${label}`}</p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-sm mr-2"
                    style={{ backgroundColor: entry.color }}
                  ></div>
                  <span className="text-gray-300 text-sm">{entry.name}:</span>
                </div>
                <span className="text-white font-medium text-sm ml-4">
                  {entry.value}%
                </span>
              </div>
            ))}
          </div>
          <div className="border-t border-gray-700 mt-2 pt-2">
            <div className="flex items-center justify-between">
              <span className="text-gray-300 text-sm">Total:</span>
              <span className="text-white font-bold text-sm">{total}%</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2 text-white">
              <TrendingUp className="w-5 h-5" />
              <span>Customer Sentiment Analysis</span>
              {isLive && <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-2"></div>}
            </CardTitle>
            <CardDescription className="text-gray-400">
              {isLiveMonitoring
                ? "Live monitoring active - tracking customer emotions in real-time"
                : "Distribution of customer emotions across all interactions"
              }
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (!isLive) {
                  startLiveMonitoring();
                } else {
                  setIsLiveMonitoring(false);
                }
                setIsLive(!isLive);
              }}
              className={`border-gray-600 ${isLive ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20' : 'bg-green-500/10 text-green-500 hover:bg-green-500/20'}`}
            >
              {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isLive ? 'Pause' : 'Live'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={resetData}
              className="border-gray-600 text-gray-300 hover:bg-gray-700"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-900/40 text-red-200 rounded-lg border border-red-700/50">
            {error}
          </div>
        )}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
              barSize={32}
              barGap={2}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" vertical={false} />
              <XAxis
                dataKey="time"
                stroke="#9CA3AF"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                stroke="#9CA3AF"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                height={36}
                iconType="circle"
                iconSize={10}
                formatter={(value) => <span className="text-gray-400 text-sm">{value}</span>}
              />
              <Bar
                dataKey="positive"
                name="Positive"
                fill="#10B981"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="neutral"
                name="Neutral"
                fill="#6366F1"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="negative"
                name="Negative"
                fill="#EF4444"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-6 flex justify-center space-x-8 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-sm"></div>
            <span className="text-gray-300">Positive</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-indigo-500 rounded-sm"></div>
            <span className="text-gray-300">Neutral</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-sm"></div>
            <span className="text-gray-300">Negative</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default InteractiveEmotionChart;