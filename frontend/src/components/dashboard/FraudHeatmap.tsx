import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChannelStatistics } from "@/services/api";

interface Transaction {
  location: string;
  isFraud: boolean;
}

interface FraudHeatmapProps {
  transactions: Transaction[];
  channelStats?: ChannelStatistics[];
}

export const FraudHeatmap = ({ transactions, channelStats }: FraudHeatmapProps) => {
  // Generate realistic Indian location data
  const mockLocationData = [
    { location: 'Mumbai', fraudRate: 9.2, count: 1547, avgAmount: 8520 },
    { location: 'Delhi', fraudRate: 10.5, count: 1432, avgAmount: 7890 },
    { location: 'Bangalore', fraudRate: 8.1, count: 1856, avgAmount: 9240 },
    { location: 'Hyderabad', fraudRate: 7.8, count: 1234, avgAmount: 6780 },
    { location: 'Chennai', fraudRate: 8.9, count: 1098, avgAmount: 7450 },
    { location: 'Kolkata', fraudRate: 9.7, count: 987, avgAmount: 6920 },
    { location: 'Pune', fraudRate: 8.4, count: 1345, avgAmount: 8100 },
    { location: 'Ahmedabad', fraudRate: 9.1, count: 876, avgAmount: 7230 },
    { location: 'International', fraudRate: 15.2, count: 234, avgAmount: 12450 },
  ];
  
  // Build location stats from transactions if available
  const locationFromTransactions = transactions.length > 0
    ? Object.values(
        transactions.reduce<Record<string, { location: string; fraudCount: number; count: number }>>((acc, txn) => {
          const key = txn.location || "Unknown";
          if (!acc[key]) {
            acc[key] = { location: key, fraudCount: 0, count: 0 };
          }
          acc[key].count += 1;
          if (txn.isFraud) {
            acc[key].fraudCount += 1;
          }
          return acc;
        }, {})
      ).map((item) => ({
        location: item.location,
        count: item.count,
        fraudRate: item.count ? (item.fraudCount / item.count) * 100 : 0,
        avgAmount: undefined,
      }))
    : [];

  const data = locationFromTransactions.length > 0
    ? locationFromTransactions
    : channelStats && channelStats.length > 0
    ? channelStats.map(stat => ({
        location: stat.channel,
        fraudRate: stat.fraud_rate,
        count: stat.total,
        avgAmount: stat.avg_amount,
      }))
    : mockLocationData;

  const sortedData = [...data].sort((a, b) => b.fraudRate - a.fraudRate);

  const getColor = (rate: number) => {
    if (rate > 12) return "bg-destructive";
    if (rate > 8) return "bg-warning";
    if (rate > 5) return "bg-accent";
    return "bg-success";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fraud Rate by Location</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {sortedData.map((item) => (
            <div
              key={item.location}
              className={`${getColor(item.fraudRate)} text-white p-4 rounded-lg transition-transform hover:scale-105 cursor-pointer`}
            >
              <div className="font-semibold text-sm mb-1">{item.location}</div>
              <div className="text-2xl font-bold">{item.fraudRate.toFixed(1)}%</div>
              <div className="text-xs opacity-90">{item.count} transactions</div>
              {('avgAmount' in item) && (
                <div className="text-xs opacity-75 mt-1">
                  ₹{Math.round(item.avgAmount).toLocaleString()} avg
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
