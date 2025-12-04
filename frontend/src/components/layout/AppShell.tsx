import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { UserButton, useUser } from "@clerk/clerk-react";
import {
  LayoutDashboard,
  LineChart,
  Brain,
  ShieldCheck,
  UploadCloud,
  Sparkles,
  Settings,
  Monitor,
  Briefcase,
  Search,
  Users,
  Activity,
  History,
  BarChart3,
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
  { label: "Results History", path: "/results-history", icon: History },
  { label: "Performance Dashboard", path: "/performance", icon: BarChart3 },
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
  const { user, isLoaded } = useUser();

  // Get user's role from Clerk metadata (default to "User" if not set)
  const userRole = (user?.publicMetadata?.role as string) || "User";

  const navItems = NAV_ITEMS.filter((item) => {
    if (!item.roles) return true;
    return item.roles.includes(userRole);
  });

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
          {isLoaded && user ? (
            <>
              <p>Logged in as</p>
              <p className="font-semibold text-foreground">{user.fullName || user.username || "User"}</p>
              <Badge variant="outline" className="mt-2 w-fit">{userRole}</Badge>
            </>
          ) : (
            <p>Loading...</p>
          )}
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
                <ThemeToggle />
                {actions}
                <UserButton 
                  afterSignOutUrl="/"
                  showName={false}
                  appearance={{
                    elements: {
                      // Avatar styling
                      userButtonAvatarBox: "h-9 w-9 ring-2 ring-primary/20 hover:ring-primary/40 transition-all",
                      userButtonTrigger: "focus:shadow-none focus:ring-2 focus:ring-primary/50",
                      // Popover card styling
                      userButtonPopoverCard: "bg-card border border-border shadow-xl rounded-xl",
                      userButtonPopoverActions: "bg-card",
                      userButtonPopoverActionButton: "text-foreground hover:bg-muted rounded-lg transition-colors",
                      userButtonPopoverActionButtonText: "text-foreground font-medium",
                      userButtonPopoverActionButtonIcon: "text-muted-foreground",
                      userButtonPopoverFooter: "hidden",
                      // User preview section
                      userPreviewMainIdentifier: "text-foreground font-semibold",
                      userPreviewSecondaryIdentifier: "text-muted-foreground text-sm",
                    }
                  }}
                  userProfileMode="modal"
                  userProfileProps={{
                    appearance: {
                      elements: {
                        // Modal container
                        modalContent: "bg-card border-border",
                        modalCloseButton: "text-muted-foreground hover:text-foreground hover:bg-muted",
                        // Card and page styling
                        card: "bg-card shadow-none border-0",
                        rootBox: "bg-card",
                        pageScrollBox: "bg-card",
                        page: "bg-card",
                        // Navbar styling
                        navbar: "bg-muted/50 border-r border-border",
                        navbarButton: "text-foreground hover:bg-muted/80 rounded-lg transition-colors",
                        navbarButtonActive: "bg-primary/10 text-primary font-medium",
                        navbarButtonIcon: "text-muted-foreground",
                        // Profile section
                        profileSectionTitle: "text-foreground font-semibold border-b border-border pb-2",
                        profileSectionTitleText: "text-foreground text-lg",
                        profileSectionContent: "bg-card",
                        profileSectionPrimaryButton: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm font-medium",
                        // Form elements
                        formButtonPrimary: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm font-medium transition-all",
                        formButtonReset: "text-muted-foreground hover:text-foreground hover:bg-muted transition-colors",
                        formFieldLabel: "text-foreground font-medium",
                        formFieldInput: "bg-background border-border text-foreground focus:ring-2 focus:ring-primary/50 focus:border-primary",
                        formFieldInputShowPasswordButton: "text-muted-foreground hover:text-foreground",
                        // Accordion and action cards
                        accordionTriggerButton: "text-foreground hover:bg-muted/50 rounded-lg",
                        accordionContent: "bg-card",
                        actionCard: "bg-muted/30 border border-border rounded-lg hover:bg-muted/50 transition-colors",
                        // Badges and alerts
                        badge: "bg-primary/10 text-primary border-primary/20 font-medium",
                        alertText: "text-foreground",
                        // Header elements
                        headerTitle: "text-foreground font-bold text-xl",
                        headerSubtitle: "text-muted-foreground",
                        // User info section
                        userPreviewMainIdentifier: "text-foreground font-semibold",
                        userPreviewSecondaryIdentifier: "text-muted-foreground",
                        // Active devices section
                        activeDeviceListItem: "bg-muted/30 border border-border rounded-lg",
                        activeDeviceIcon: "text-muted-foreground",
                        // Footer and breadcrumbs
                        footer: "hidden",
                        footerAction: "hidden",
                        breadcrumbs: "text-muted-foreground",
                        breadcrumbsItem: "text-foreground hover:text-primary transition-colors",
                        breadcrumbsItemDivider: "text-muted-foreground",
                        // Internal cards
                        profilePage: "bg-card",
                        accountSwitcherTrigger: "bg-muted/30 border-border hover:bg-muted/50",
                        identityPreview: "bg-muted/20 rounded-lg p-3",
                        identityPreviewEditButton: "text-primary hover:text-primary/80",
                        // Connected accounts
                        socialButtonsBlockButton: "bg-muted/30 border border-border text-foreground hover:bg-muted/50",
                        socialButtonsBlockButtonText: "text-foreground font-medium",
                        // Delete button (danger)
                        formButtonReset__danger: "text-destructive hover:bg-destructive/10",
                      }
                    }
                  }}
                />
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