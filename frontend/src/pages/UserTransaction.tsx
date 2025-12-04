import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Shield, AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { detectFraudComprehensive } from "@/services/api";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { UserButton, useUser } from "@clerk/clerk-react";

interface TransactionRequest {
  customer_id: string;
  amount: number;
  channel: string;
  hour: number;
  account_age_days: number;
  kyc_verified: string;
}

interface TransactionResponse {
  transaction_id: string;
  customer_id: string;
  prediction: string;
  is_fraud: number;
  risk_score: number;
  fraud_probability: number;
  risk_level: string;
  confidence: number;
  explanation?: string;
  rule_flags: string[];
  behavioral_flags: string[];
  signature_flags: string[];
  velocity_flags: string[];
  all_flags: string[];
  alerts_generated: number;
  alert_ids: string[];
  risk_factors: string[];
  customer_risk_profile: any;
}

const UserTransactionPage = () => {
  const { user } = useUser();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TransactionResponse | null>(null);
  const [formData, setFormData] = useState<TransactionRequest>({
    customer_id: user?.id || "",
    account_age_days: 365,
    amount: 5000,
    channel: "Mobile",
    kyc_verified: "Yes",
    hour: new Date().getHours(),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await detectFraudComprehensive(formData);
      setResult(response);
      
      if (response.prediction === "Fraud") {
        toast.error("⚠️ Transaction Flagged - Security Review Required!");
      } else {
        toast.success("✓ Transaction Approved - Processing...");
      }
    } catch (error: any) {
      console.error("Transaction error:", error);
      toast.error("Failed to process transaction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof TransactionRequest, value: any) => {
    if (field === 'account_age_days' || field === 'amount' || field === 'hour') {
      const numValue = parseFloat(value);
      setFormData(prev => ({ ...prev, [field]: isNaN(numValue) ? 0 : numValue }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const getRiskColor = (prediction: string) => {
    if (prediction === "Fraud") return "border-red-500 bg-red-50 dark:bg-red-950/30";
    return "border-green-500 bg-green-50 dark:bg-green-950/30";
  };

  const getRiskIcon = (prediction: string) => {
    return prediction === "Fraud" 
      ? <AlertTriangle className="h-12 w-12 text-red-600" />
      : <CheckCircle className="h-12 w-12 text-green-600" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <Shield className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">TransIntelliFlow</h1>
              <p className="text-xs text-muted-foreground">Secure Transaction Portal</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right mr-3">
              <p className="text-sm font-medium">{user?.fullName || user?.username}</p>
              <Badge variant="outline" className="text-xs">User</Badge>
            </div>
            <ThemeToggle />
            <UserButton 
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  userButtonAvatarBox: "h-9 w-9 ring-2 ring-primary/20 hover:ring-primary/40 transition-all",
                  userButtonPopoverCard: "bg-card border border-border shadow-xl rounded-xl",
                  userButtonPopoverActionButton: "text-foreground hover:bg-muted rounded-lg",
                  userButtonPopoverActionButtonText: "text-foreground font-medium",
                  userButtonPopoverFooter: "hidden",
                }
              }}
              userProfileMode="modal"
              userProfileProps={{
                appearance: {
                  elements: {
                    modalContent: "bg-card border-border",
                    card: "bg-card shadow-none border-0",
                    navbar: "bg-muted/50 border-r border-border",
                    navbarButton: "text-foreground hover:bg-muted/80 rounded-lg",
                    navbarButtonActive: "bg-primary/10 text-primary font-medium",
                    profileSectionTitle: "text-foreground font-semibold border-b border-border pb-2",
                    formButtonPrimary: "bg-primary text-primary-foreground hover:bg-primary/90",
                    formFieldInput: "bg-background border-border text-foreground focus:ring-2 focus:ring-primary/50",
                    badge: "bg-primary/10 text-primary border-primary/20",
                    activeDeviceListItem: "bg-muted/30 border border-border rounded-lg",
                    footer: "hidden",
                  }
                }
              }}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Submit Transaction</h2>
          <p className="text-muted-foreground">
            Enter your transaction details below. All transactions are monitored for security.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Transaction Form */}
          <Card>
            <CardHeader>
              <CardTitle>Transaction Details</CardTitle>
              <CardDescription>Fill in the details of your transaction</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="customer_id">Customer ID</Label>
                  <Input
                    id="customer_id"
                    value={formData.customer_id}
                    onChange={(e) => handleInputChange('customer_id', e.target.value)}
                    placeholder="Enter your customer ID"
                    required
                    disabled
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="amount">Transaction Amount (₹)</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={formData.amount}
                    onChange={(e) => handleInputChange('amount', e.target.value)}
                    min="1"
                    step="0.01"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="channel">Channel</Label>
                  <Select
                    value={formData.channel}
                    onValueChange={(value) => handleInputChange('channel', value)}
                  >
                    <SelectTrigger id="channel">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Mobile">Mobile Banking</SelectItem>
                      <SelectItem value="Web">Web Banking</SelectItem>
                      <SelectItem value="ATM">ATM</SelectItem>
                      <SelectItem value="POS">Point of Sale</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="account_age_days">Account Age (Days)</Label>
                  <Input
                    id="account_age_days"
                    type="number"
                    value={formData.account_age_days}
                    onChange={(e) => handleInputChange('account_age_days', e.target.value)}
                    min="0"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="kyc_verified">KYC Status</Label>
                  <Select
                    value={formData.kyc_verified}
                    onValueChange={(value) => handleInputChange('kyc_verified', value)}
                  >
                    <SelectTrigger id="kyc_verified">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Yes">Verified</SelectItem>
                      <SelectItem value="No">Not Verified</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button type="submit" className="w-full" size="lg" disabled={loading}>
                  {loading ? (
                    "Processing..."
                  ) : (
                    <>
                      Submit Transaction
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Status Card */}
                <Card className={`border-2 ${getRiskColor(result.prediction)}`}>
                  <CardContent className="pt-6">
                    <div className="flex flex-col items-center text-center space-y-4">
                      {getRiskIcon(result.prediction)}
                      <div>
                        <h3 className="text-2xl font-bold mb-1">
                          {result.prediction === "Fraud" ? "Transaction Flagged" : "Transaction Approved"}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {result.prediction === "Fraud" 
                            ? "This transaction requires security review"
                            : "Your transaction has been approved"
                          }
                        </p>
                      </div>
                      <div className="w-full grid grid-cols-2 gap-4 pt-4 border-t">
                        <div>
                          <p className="text-xs text-muted-foreground">Risk Score</p>
                          <p className="text-xl font-bold">{(result.risk_score * 100).toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Risk Level</p>
                          <Badge variant={result.risk_level === "High" || result.risk_level === "Critical" ? "destructive" : "outline"}>
                            {result.risk_level}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Explanation */}
                {result.explanation && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Transaction Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {result.explanation}
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Risk Factors */}
                {result.risk_factors && result.risk_factors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Identified Factors</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {result.risk_factors.map((factor, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <span className="text-warning mt-0.5">⚠</span>
                            <span>{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Transaction ID */}
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Transaction ID</p>
                      <p className="text-sm font-mono font-medium">{result.transaction_id}</p>
                      {result.alert_ids && result.alert_ids.length > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-xs text-muted-foreground mb-1">Alert Generated</p>
                          <Badge variant="outline" className="font-mono text-xs">
                            {result.alert_ids[0]}
                          </Badge>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="border-dashed">
                <CardContent className="pt-6">
                  <div className="text-center text-muted-foreground py-12">
                    <Shield className="h-16 w-16 mx-auto mb-4 opacity-20" />
                    <p className="text-sm">Submit a transaction to see results</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default UserTransactionPage;
