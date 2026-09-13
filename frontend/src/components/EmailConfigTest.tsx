import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const EmailConfigTest = () => {
  const [config, setConfig] = useState({
    email: '',
    appPassword: '',
    telegramUserId: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult('Submitting...');

    try {
      console.log('Sending request with config:', config);
      
      const response = await fetch('https://customer-sentiment-te99.onrender.com/api/email-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      console.log('Response status:', response.status);

      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        setResult('Success: ' + JSON.stringify(data));
      } else {
        setResult('Error: ' + JSON.stringify(data));
      }

    } catch (error) {
      console.error('Request error:', error);
      setResult('Request failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const testGet = async () => {
    try {
      const response = await fetch('https://customer-sentiment-te99.onrender.com/api/email-config');
      const data = await response.json();
      setResult('GET result: ' + JSON.stringify(data));
    } catch (error) {
      setResult('GET error: ' + error.message);
    }
  };

  return (
    <div className="p-8 max-w-md mx-auto">
      <h1 className="text-2xl mb-4">Email Config Test</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label>Email</Label>
          <Input
            value={config.email}
            onChange={(e) => setConfig(prev => ({ ...prev, email: e.target.value }))}
            placeholder="test@gmail.com"
          />
        </div>
        
        <div>
          <Label>App Password</Label>
          <Input
            value={config.appPassword}
            onChange={(e) => setConfig(prev => ({ ...prev, appPassword: e.target.value }))}
            placeholder="app password"
          />
        </div>
        
        <div>
          <Label>Telegram User ID</Label>
          <Input
            value={config.telegramUserId}
            onChange={(e) => setConfig(prev => ({ ...prev, telegramUserId: e.target.value }))}
            placeholder="123456789"
          />
        </div>
        
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Config'}
        </Button>
      </form>

      <Button onClick={testGet} className="mt-4 w-full" variant="outline">
        Test GET Endpoint
      </Button>

      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <pre className="text-sm">{result}</pre>
        </div>
      )}
    </div>
  );
};

export default EmailConfigTest;
