import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  Clock,
  Search,
  Filter,
  Eye,
  Check,
  X,
  Shield,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

interface Alert {
  id: string;
  transaction_id: string;
  customer_id: string;
  timestamp: string;
  amount: number;
  channel: string;
  risk_level: "High" | "Medium" | "Low";
  fraud_probability: number;
  status: "pending" | "acknowledged" | "resolved" | "false_positive";
  message: string;
  risk_factors: string[];
}

const AlertsPage = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [riskFilter, setRiskFilter] = useState("all");
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  useEffect(() => {
    loadAlerts();
    // Simulate real-time updates every 10 seconds
    const interval = setInterval(loadAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // Simulated alerts data
      const mockAlerts: Alert[] = [
        {
          id: "ALT001",
          transaction_id: "TXN001234",
          customer_id: "CUST5678",
          timestamp: new Date().toISOString(),
          amount: 45000,
          channel: "Mobile",
          risk_level: "High",
          fraud_probability: 0.92,
          status: "pending",
          message: "High-value transaction from new device",
          risk_factors: [
            "High transaction amount (₹45,000)",
            "New device detected",
            "Unusual time (2:30 AM)",
            "Different geolocation"
          ]
        },
        {
          id: "ALT002",
          transaction_id: "TXN001235",
          customer_id: "CUST5679",
          timestamp: new Date(Date.now() - 300000).toISOString(),
          amount: 12000,
          channel: "ATM",
          risk_level: "Medium",
          fraud_probability: 0.68,
          status: "acknowledged",
          message: "Multiple ATM withdrawals in short time",
          risk_factors: [
            "3 transactions in 10 minutes",
            "Different ATM locations",
            "Account age < 30 days"
          ]
        },
        {
          id: "ALT003",
          transaction_id: "TXN001236",
          customer_id: "CUST5680",
          timestamp: new Date(Date.now() - 600000).toISOString(),
          amount: 25000,
          channel: "Web",
          risk_level: "High",
          fraud_probability: 0.85,
          status: "resolved",
          message: "Confirmed fraud - Account locked",
          risk_factors: [
            "KYC not verified",
            "High-value transaction",
            "Suspicious merchant"
          ]
        }
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error("Failed to load alerts:", error);
      toast.error("Failed to load alerts");
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, status: "acknowledged" } : alert
    ));
    toast.success("Alert acknowledged");
  };

  const handleResolve = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, status: "resolved" } : alert
    ));
    toast.success("Alert resolved");
  };

  const handleMarkFalsePositive = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, status: "false_positive" } : alert
    ));
    toast.success("Marked as false positive");
  };

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.customer_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || alert.status === statusFilter;
    const matchesRisk = riskFilter === "all" || alert.risk_level === riskFilter;
    return matchesSearch && matchesStatus && matchesRisk;
  });

  const pendingCount = alerts.filter(a => a.status === "pending").length;
  const highRiskCount = alerts.filter(a => a.risk_level === "High" && a.status === "pending").length;

  const getRiskColor = (level: string) => {
    switch (level) {
      case "High": return "text-red-500 bg-red-500/10";
      case "Medium": return "text-yellow-500 bg-yellow-500/10";
      case "Low": return "text-blue-500 bg-blue-500/10";
      default: return "text-gray-500 bg-gray-500/10";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "destructive";
      case "acknowledged": return "default";
      case "resolved": return "outline";
      case "false_positive": return "secondary";
      default: return "default";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/dashboard">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Bell className="h-6 w-6 text-primary" />
                  Alerts & Notifications
                </h1>
                <p className="text-sm text-muted-foreground">Real-time fraud alert management</p>
              </div>
            </div>
            
            <Button size="sm" onClick={loadAlerts}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Pending Alerts</p>
                  <p className="text-3xl font-bold">{pendingCount}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">High Risk</p>
                  <p className="text-3xl font-bold">{highRiskCount}</p>
                </div>
                <Shield className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Alerts</p>
                  <p className="text-3xl font-bold">{alerts.length}</p>
                </div>
                <Bell className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by transaction ID or customer ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="acknowledged">Acknowledged</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="false_positive">False Positive</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={riskFilter} onValueChange={setRiskFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Risk Levels</SelectItem>
                  <SelectItem value="High">High Risk</SelectItem>
                  <SelectItem value="Medium">Medium Risk</SelectItem>
                  <SelectItem value="Low">Low Risk</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Alerts List */}
        <div className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="py-12 text-center">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                <p className="mt-2 text-muted-foreground">Loading alerts...</p>
              </CardContent>
            </Card>
          ) : filteredAlerts.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Bell className="h-12 w-12 mx-auto text-muted-foreground" />
                <p className="mt-4 text-muted-foreground">No alerts found</p>
              </CardContent>
            </Card>
          ) : (
            filteredAlerts.map((alert) => (
              <Card key={alert.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{alert.transaction_id}</CardTitle>
                        <Badge variant={getStatusColor(alert.status)} className="text-xs">
                          {alert.status.replace("_", " ").toUpperCase()}
                        </Badge>
                      </div>
                      <CardDescription>
                        Customer: {alert.customer_id} • {new Date(alert.timestamp).toLocaleString()}
                      </CardDescription>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge className={getRiskColor(alert.risk_level)}>
                        {alert.risk_level} Risk
                      </Badge>
                      <span className="text-sm font-mono">
                        {(alert.fraud_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 text-sm">
                      <span className="font-semibold">Amount:</span>
                      <span className="text-lg">₹{alert.amount.toLocaleString()}</span>
                      <span className="text-muted-foreground">•</span>
                      <span>Channel: {alert.channel}</span>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium mb-2">{alert.message}</p>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">Risk Factors:</p>
                        {alert.risk_factors.map((factor, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                            <span>{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {alert.status === "pending" && (
                      <div className="flex gap-2 pt-2">
                        <Button size="sm" variant="outline" onClick={() => handleAcknowledge(alert.id)}>
                          <Eye className="h-4 w-4 mr-2" />
                          Acknowledge
                        </Button>
                        <Button size="sm" variant="default" onClick={() => handleResolve(alert.id)}>
                          <Check className="h-4 w-4 mr-2" />
                          Resolve
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => handleMarkFalsePositive(alert.id)}>
                          <X className="h-4 w-4 mr-2" />
                          False Positive
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  );
};

export default AlertsPage;
