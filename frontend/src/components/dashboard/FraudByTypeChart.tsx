import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChannelStatistics } from "@/services/api";

interface FraudByTypeChartProps {
  channelStats?: ChannelStatistics[];
}

export const FraudByTypeChart = ({ channelStats }: FraudByTypeChartProps) => {
  // If no real data, generate realistic mock data for Indian banking channels
  const mockData = !channelStats || channelStats.length === 0 ? [
    { channel: 'Mobile', total: 2547, fraud: 228, fraud_rate: 8.95 },
    { channel: 'ATM', total: 1832, fraud: 183, fraud_rate: 9.99 },
    { channel: 'Web', total: 2156, fraud: 216, fraud_rate: 10.02 },
    { channel: 'POS', total: 1465, fraud: 117, fraud_rate: 7.99 },
  ] : channelStats;
  
  const data = mockData.map(stat => {
    const fraudCount = Math.floor((stat as any).fraud_count ?? (stat.total * stat.fraud_rate / 100));
    const legitCount = Math.max(0, stat.total - fraudCount);
    return {
      type: stat.channel,
      fraudRate: parseFloat(stat.fraud_rate.toFixed(1)),
      fraudCount,
      legitimateCount: legitCount,
      count: stat.total,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fraud by Channel</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="type" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" label={{ value: "Transaction Count", angle: -90, position: "insideLeft" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
            />
            <Legend />
            <Bar dataKey="fraudCount" fill="hsl(var(--destructive))" name="Fraud" stackId="a" />
            <Bar dataKey="legitimateCount" fill="hsl(var(--success))" name="Legitimate" stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
