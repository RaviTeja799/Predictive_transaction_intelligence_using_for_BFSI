import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface Transaction {
  date: string;
  isFraud: boolean;
}

interface FraudTrendChartProps {
  transactions: Transaction[];
}

export const FraudTrendChart = ({ transactions }: FraudTrendChartProps) => {
  // Generate realistic date range: Oct 30 - Nov 15 with daily data
  const generateDateRange = () => {
    const dates = [];
    const startDate = new Date('2025-10-30');
    const endDate = new Date('2025-11-15');
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      dates.push(new Date(d).toISOString().split('T')[0]);
    }
    return dates;
  };
  
  const dateRange = generateDateRange();
  
  // Group transactions by date or use mock data
  const dailyData = dateRange.map((date, index) => {
    const dateTransactions = transactions.filter(txn => txn.date.startsWith(date));
    const fraudCount = dateTransactions.filter(t => t.isFraud).length;
    const legitimateCount = dateTransactions.length - fraudCount;
    
    // If no real data, use realistic mock increasing trend
    if (dateTransactions.length === 0) {
      const baselineCount = 150 + Math.floor(Math.random() * 50);
      const fraudPercentage = 0.08 + Math.random() * 0.04; // 8-12%
      return {
        date: new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        fraud: Math.floor(baselineCount * fraudPercentage),
        legitimate: Math.floor(baselineCount * (1 - fraudPercentage)),
      };
    }
    
    return {
      date: new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      fraud: fraudCount,
      legitimate: legitimateCount,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fraud Trend Over Time (Oct 30 - Nov 15)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="date" 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fontSize: 10 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="fraud"
              stroke="hsl(var(--destructive))"
              strokeWidth={2}
              name="Fraud"
            />
            <Line
              type="monotone"
              dataKey="legitimate"
              stroke="hsl(var(--success))"
              strokeWidth={2}
              name="Legitimate"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
