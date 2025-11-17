import { FormEvent, useMemo, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { uploadBatchPrediction, BatchPredictionResponse } from "@/services/api";
import { toast } from "sonner";
import { Download, UploadCloud, FileDown } from "lucide-react";

const REQUIRED_HEADERS = [
  "customer_id",
  "transaction_amount",
  "account_age_days",
  "channel",
  "kyc_verified",
  "hour",
];

const BatchPredictionPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BatchPredictionResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      toast.error("Please select a CSV file");
      return;
    }
    setUploading(true);
    setProgress(5);
    try {
      const response = await uploadBatchPrediction(file);
      setResult(response);
      setProgress(100);
      toast.success("Batch processed successfully");
    } catch (error: any) {
      console.error("Batch prediction failed", error);
      toast.error(error?.response?.data?.detail || "Upload failed. Check CSV format.");
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 1200);
    }
  };

  const handleDownloadTemplate = () => {
    const header = REQUIRED_HEADERS.join(",");
    const sampleRows = [
      "CUST1001,12500,420,Mobile,Yes,14",
      "CUST1002,52000,21,ATM,No,2",
    ];
    const blob = new Blob([[header, ...sampleRows].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "batch_template.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadResults = () => {
    if (!result) return;
    const header = "transaction_id,prediction,fraud_probability,risk_level,confidence";
    const rows = result.results.map((row) =>
      [
        row.transaction_id,
        row.prediction,
        row.fraud_probability,
        row.risk_level,
        row.confidence,
      ].join(",")
    );
    const blob = new Blob([[header, ...rows].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result.batch_id}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const summary = useMemo(() => {
    if (!result) return null;
    const fraudRate = result.total_records
      ? ((result.fraudulent_predictions / result.total_records) * 100).toFixed(2)
      : "0";
    return {
      fraudRate,
      avgProbability: result.average_fraud_probability.toFixed(2),
    };
  }, [result]);

  return (
    <AppShell
      title="Batch Predictions"
      subtitle="Upload large volumes for bulk inference"
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
            <Download className="mr-2 h-4 w-4" />
            Template
          </Button>
          {result && (
            <Button size="sm" variant="secondary" onClick={handleDownloadResults}>
              <FileDown className="mr-2 h-4 w-4" />
              Results CSV
            </Button>
          )}
        </div>
      }
    >
      <Card>
        <CardHeader>
          <CardTitle>Upload CSV</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleUpload}>
            <div className="space-y-2">
              <Label htmlFor="csv">Select CSV file</Label>
              <Input
                id="csv"
                type="file"
                accept=".csv"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
            </div>
            <p className="text-sm text-muted-foreground">
              Required headers: {REQUIRED_HEADERS.join(", ")}
            </p>
            <Button type="submit" disabled={uploading}>
              {uploading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-b-2 border-white" />
                  Uploading...
                </>
              ) : (
                <>
                  <UploadCloud className="mr-2 h-4 w-4" />
                  Run Batch Prediction
                </>
              )}
            </Button>
            {progress > 0 && (
              <div className="space-y-2">
                <Progress value={progress} />
                <p className="text-xs text-muted-foreground">{progress}% processed</p>
              </div>
            )}
          </form>
        </CardContent>
      </Card>

      {result && summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Total Records</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-bold">
              {result.total_records.toLocaleString()}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Fraudulent Predictions</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-bold text-destructive">
              {result.fraudulent_predictions.toLocaleString()} ({summary.fraudRate}%)
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Avg Fraud Probability</CardTitle>
            </CardHeader>
            <CardContent className="text-3xl font-bold">
              {summary.avgProbability}%
            </CardContent>
          </Card>
        </div>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Batch Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>#</TableHead>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Prediction</TableHead>
                    <TableHead>Fraud Probability</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Confidence</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.results.map((row) => (
                    <TableRow key={row.transaction_id}>
                      <TableCell>{row.row}</TableCell>
                      <TableCell className="font-mono">{row.transaction_id}</TableCell>
                      <TableCell>
                        <Badge variant={row.prediction === "Fraud" ? "destructive" : "default"}>
                          {row.prediction}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.fraud_probability}%</TableCell>
                      <TableCell>{row.risk_level}</TableCell>
                      <TableCell>{row.confidence.toFixed(2)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </AppShell>
  );
};

export default BatchPredictionPage;
