import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Button } from "@/components/ui/button";

const API_BASE = 'https://customer-sentiment-te99.onrender.com';

interface OverviewItem {
    count: number;
    percentage_text: string;
}

interface TrendPoint {
    time: string;
    anger: number;
    confusion: number;
    joy: number;
    neutral: number;
}

const SentimentDashboard = () => {
    const [overview, setOverview] = useState<{[k: string]: OverviewItem}>({});
    const [trends, setTrends] = useState<TrendPoint[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchOverview = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/historical/overview`);
            if (response.ok) {
                const data = await response.json();
                setOverview(data);
            } else {
                setError("Failed to fetch overview");
            }
        } catch (err) {
            setError("Error fetching overview");
        }
    };

    const fetchTrends = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/historical/trends?hours=12`);
            if (response.ok) {
                const data = await response.json();
                setTrends(data.trends || []);
            } else {
                setError("Failed to fetch trends");
            }
        } catch (err) {
            setError("Error fetching trends");
        }
    };

    const runBackfill = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/historical/analyze-missing`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const result = await response.json();
                alert(`Backfill completed: ${result.updated} documents updated, ${result.errors} errors`);
                // Refresh data
                await fetchOverview();
                await fetchTrends();
            } else {
                setError("Backfill failed");
            }
        } catch (err) {
            setError("Error running backfill");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOverview();
        fetchTrends();
    }, []);

    const getEmotionColor = (emotion: string) => {
        switch (emotion) {
            case 'anger': return '#ef4444';
            case 'joy': return '#10b981';
            case 'confusion': return '#f59e0b';
            case 'neutral': return '#6b7280';
            default: return '#6b7280';
        }
    };

    const getEmotionIcon = (emotion: string) => {
        switch (emotion) {
            case 'anger': return <AlertTriangle className="h-4 w-4 text-red-500" />;
            case 'joy': return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'confusion': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
            case 'neutral': return <TrendingUp className="h-4 w-4 text-gray-500" />;
            default: return <TrendingUp className="h-4 w-4 text-gray-500" />;
        }
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Chat & Ticket Sentiment Dashboard</h1>
                <Button onClick={runBackfill} disabled={loading}>
                    {loading ? "Running..." : "Run Sentiment Backfill"}
                </Button>
            </div>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            )}

            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.entries(overview).map(([emotion, data]) => (
                    <Card key={emotion}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium capitalize">
                                {emotion}
                            </CardTitle>
                            {getEmotionIcon(emotion)}
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{data.count}</div>
                            <p className="text-xs text-muted-foreground">
                                {data.percentage_text}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Trends Chart */}
            <Card>
                <CardHeader>
                    <CardTitle>Sentiment Trends (Last 12 Hours)</CardTitle>
                    <CardDescription>
                        Hourly breakdown of sentiment distribution
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={trends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="anger" fill="#ef4444" />
                            <Bar dataKey="confusion" fill="#f59e0b" />
                            <Bar dataKey="joy" fill="#10b981" />
                            <Bar dataKey="neutral" fill="#6b7280" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    );
};

export default SentimentDashboard; 