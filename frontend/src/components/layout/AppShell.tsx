import { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/context/AuthContext";
import {
  LayoutDashboard,
  LineChart,
  Brain,
  SlidersHorizontal,
  ShieldCheck,
  UploadCloud,
  Sparkles,
  Settings,
  Monitor,
  Briefcase,
  Search,
  Users,
  Activity,
} from "lucide-react";

interface AppShellProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: string[];
}

const NAV_ITEMS: NavItem[] = [
  { label: "Home Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Analytics & Reports", path: "/analytics", icon: LineChart },
  { label: "Batch Predictions", path: "/batch-prediction", icon: UploadCloud },
  { label: "Simulation Lab", path: "/simulation-lab", icon: Sparkles },
  { label: "Model Testing", path: "/predict", icon: Brain },
  { label: "Modeling Workspace", path: "/modeling", icon: Activity },
  { label: "Transaction Search", path: "/search", icon: Search },
  { label: "Customer 360", path: "/customer360", icon: Users },
  { label: "Case Management", path: "/cases", icon: Briefcase },
  { label: "Monitoring Wall", path: "/monitoring", icon: Monitor },
  { label: "Settings", path: "/settings", icon: Settings },
  { label: "Admin & Health", path: "/admin", icon: ShieldCheck, roles: ["Administrator"] },
];

const AppShell = ({ title, subtitle, actions, children }: AppShellProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navItems = NAV_ITEMS.filter((item) => {
    if (!item.roles || !user) return true;
    return item.roles.includes(user.role);
  });

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const renderNavContent = () => (
    <div className="space-y-1">
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = location.pathname.startsWith(item.path);
        return (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:text-primary hover:bg-primary/5"
            )}
          >
            <Icon className="h-4 w-4" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </div>
  );

  return (
    <div className="min-h-screen bg-muted/20 text-foreground flex">
      <aside className="hidden lg:flex w-64 flex-col border-r bg-background/95">
        <div className="px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <ShieldCheck className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">TransIntelliFlow</p>
              <p className="text-lg font-bold">Control Center</p>
            </div>
          </div>
        </div>
        <Separator />
        <ScrollArea className="flex-1 px-4 py-4">
          {renderNavContent()}
        </ScrollArea>
        <div className="px-4 py-4 text-sm text-muted-foreground">
          <p>Logged in as</p>
          <p className="font-semibold text-foreground">{user?.name || "Guest"}</p>
          {user && <Badge variant="outline" className="mt-2 w-fit">{user.role}</Badge>}
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex flex-col gap-4 px-4 py-4 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-muted-foreground">Operational Intelligence</p>
                <h1 className="text-2xl font-bold">{title}</h1>
                {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
              </div>
              <div className="flex items-center gap-3">
                {actions}
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <SlidersHorizontal className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              </div>
            </div>
            <div className="lg:hidden">
              <ScrollArea className="rounded-md border">
                <div className="flex gap-2 px-4 py-2">
                  {navItems.map((item) => {
                    const active = location.pathname.startsWith(item.path);
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        className={cn(
                          "whitespace-nowrap rounded-full px-4 py-1 text-xs font-medium",
                          active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                        )}
                      >
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              </ScrollArea>
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 py-6 lg:px-8">
          <div className="space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppShell;
