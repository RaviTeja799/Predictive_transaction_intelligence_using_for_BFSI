import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle,
  Clock,
  MapPin,
  CreditCard,
  User,
  Calendar,
  Shield,
  RefreshCw,
  Download,
  Flag,
} from "lucide-react";
import { toast } from "sonner";

interface TransactionDetail {
  transaction_id: string;
  customer_id: string;
  timestamp: string;
  amount: number;
  channel: string;
  kyc_verified: string;
  account_age_days: number;
  hour: number;
  is_fraud: number;
  fraud_probability?: number;
  risk_level?: string;
  device_info?: {
    type: string;
    os: string;
    browser: string;
    ip_address: string;
  };
  location?: {
    city: string;
    state: string;
    country: string;
    coordinates: { lat: number; lng: number };
  };
}

const TransactionDetailsPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState<TransactionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [relatedTransactions, setRelatedTransactions] = useState<TransactionDetail[]>([]);

  useEffect(() => {
    loadTransactionDetails();
  }, [id]);

  const loadTransactionDetails = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // Simulated transaction detail
      const mockTransaction: TransactionDetail = {
        transaction_id: id || "TXN001234",
        customer_id: "CUST5678",
        timestamp: new Date().toISOString(),
        amount: 45000,
        channel: "Mobile",
        kyc_verified: "Yes",
        account_age_days: 180,
        hour: 14,
        is_fraud: 1,
        fraud_probability: 0.92,
        risk_level: "High",
        device_info: {
          type: "Mobile",
          os: "Android 13",
          browser: "Chrome Mobile 120",
          ip_address: "103.25.45.67"
        },
        location: {
          city: "Mumbai",
          state: "Maharashtra",
          country: "India",
          coordinates: { lat: 19.0760, lng: 72.8777 }
        }
      };
      
      setTransaction(mockTransaction);
      
      // Mock related transactions
      setRelatedTransactions([
        { ...mockTransaction, transaction_id: "TXN001233", amount: 5000, is_fraud: 0 },
        { ...mockTransaction, transaction_id: "TXN001232", amount: 3500, is_fraud: 0 },
      ]);
    } catch (error) {
      console.error("Failed to load transaction details:", error);
      toast.error("Failed to load transaction details");
    } finally {
      setLoading(false);
    }
  };

  const handleFlag = () => {
    toast.success("Transaction flagged for review");
  };

  const handleExport = () => {
    toast.success("Exporting transaction report");
  };

  if (loading || !transaction) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <RefreshCw className="h-12 w-12 animate-spin mx-auto text-primary" />
          <p className="text-lg text-muted-foreground">Loading transaction details...</p>
        </div>
      </div>
    );
  }

  const riskColor = transaction.risk_level === "High" ? "text-red-500" :
                   transaction.risk_level === "Medium" ? "text-yellow-500" : "text-green-500";

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Transaction Details</h1>
                <p className="text-sm text-muted-foreground">{transaction.transaction_id}</p>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={handleFlag}>
                <Flag className="h-4 w-4 mr-2" />
                Flag
              </Button>
              <Button size="sm" variant="outline" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Status Banner */}
        <Card className={transaction.is_fraud ? "border-red-500" : "border-green-500"}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {transaction.is_fraud ? (
                  <AlertTriangle className="h-12 w-12 text-red-500" />
                ) : (
                  <CheckCircle className="h-12 w-12 text-green-500" />
                )}
                <div>
                  <h2 className="text-2xl font-bold">
                    {transaction.is_fraud ? "Fraudulent Transaction" : "Legitimate Transaction"}
                  </h2>
                  <p className="text-muted-foreground">
                    Confidence: {((transaction.fraud_probability || 0) * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-3xl font-bold">₹{transaction.amount.toLocaleString()}</p>
                <Badge className={riskColor}>
                  {transaction.risk_level} Risk
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Details Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="customer">Customer</TabsTrigger>
            <TabsTrigger value="technical">Technical</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Transaction Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">Timestamp</p>
                      <p className="font-medium">{new Date(transaction.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">Channel</p>
                      <p className="font-medium">{transaction.channel}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Shield className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">KYC Status</p>
                      <Badge variant={transaction.kyc_verified === "Yes" ? "default" : "destructive"}>
                        {transaction.kyc_verified === "Yes" ? "Verified" : "Not Verified"}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">Transaction Hour</p>
                      <p className="font-medium">{transaction.hour}:00</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Location & Device</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-3">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">Location</p>
                      <p className="font-medium">
                        {transaction.location?.city}, {transaction.location?.state}
                      </p>
                      <p className="text-xs text-muted-foreground">{transaction.location?.country}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">Device</p>
                      <p className="font-medium">{transaction.device_info?.type}</p>
                      <p className="text-xs text-muted-foreground">{transaction.device_info?.os}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Shield className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">IP Address</p>
                      <p className="font-mono text-sm">{transaction.device_info?.ip_address}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="customer">
            <Card>
              <CardHeader>
                <CardTitle>Customer Information</CardTitle>
                <CardDescription>Details about the customer associated with this transaction</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Customer ID</p>
                    <p className="font-mono font-medium">{transaction.customer_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Account Age</p>
                    <p className="font-medium">{transaction.account_age_days} days</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">KYC Status</p>
                    <Badge variant={transaction.kyc_verified === "Yes" ? "default" : "destructive"}>
                      {transaction.kyc_verified === "Yes" ? "Verified" : "Not Verified"}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Risk Profile</p>
                    <Badge className={riskColor}>{transaction.risk_level}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="technical">
            <Card>
              <CardHeader>
                <CardTitle>Technical Details</CardTitle>
                <CardDescription>Device and network information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Browser</p>
                    <p className="font-medium">{transaction.device_info?.browser}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Operating System</p>
                    <p className="font-medium">{transaction.device_info?.os}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Device Type</p>
                    <p className="font-medium">{transaction.device_info?.type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">IP Address</p>
                    <p className="font-mono text-sm">{transaction.device_info?.ip_address}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>Related Transactions</CardTitle>
                <CardDescription>Recent transactions from the same customer</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {relatedTransactions.map((txn) => (
                    <div key={txn.transaction_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        {txn.is_fraud ? (
                          <AlertTriangle className="h-5 w-5 text-red-500" />
                        ) : (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        )}
                        <div>
                          <p className="font-mono text-sm">{txn.transaction_id}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(txn.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">₹{txn.amount.toLocaleString()}</p>
                        <Badge variant={txn.is_fraud ? "destructive" : "default"} className="text-xs">
                          {txn.is_fraud ? "Fraud" : "Legitimate"}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default TransactionDetailsPage;
