import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import DashboardNew from "./pages/DashboardNew";
import Prediction from "./pages/Prediction";
import AlertsPage from "./pages/AlertsPage";
import TransactionDetailsPage from "./pages/TransactionDetailsPage";
import AnalyticsReports from "./pages/AnalyticsReports";
import BatchPredictionPage from "./pages/BatchPrediction";
import SimulationLab from "./pages/SimulationLab";
import LoginPage from "./pages/Login";
import NotFound from "./pages/NotFound";
import SettingsPage from "./pages/Settings";
import MonitoringWall from "./pages/MonitoringWall";
import CaseManagement from "./pages/CaseManagement";
import ModelingWorkspace from "./pages/ModelingWorkspace";
import TransactionSearch from "./pages/TransactionSearch";
import Customer360 from "./pages/Customer360";
import AdminHealth from "./pages/AdminHealth";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { AuthProvider } from "@/context/AuthContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardNew />} />
              <Route path="/dashboard-old" element={<Dashboard />} />
              <Route path="/predict" element={<Prediction />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/transaction/:id" element={<TransactionDetailsPage />} />
              <Route path="/analytics" element={<AnalyticsReports />} />
              <Route path="/batch-prediction" element={<BatchPredictionPage />} />
              <Route path="/simulation-lab" element={<SimulationLab />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/monitoring" element={<MonitoringWall />} />
              <Route path="/cases" element={<CaseManagement />} />
              <Route path="/modeling" element={<ModelingWorkspace />} />
              <Route path="/search" element={<TransactionSearch />} />
              <Route path="/customer360" element={<Customer360 />} />
              <Route path="/admin" element={<AdminHealth />} />
            </Route>
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
