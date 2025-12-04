import { UserProfile } from "@clerk/clerk-react";
import { Shield, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";

const ProfilePage = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Shield className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">TransIntelliFlow</span>
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/dashboard">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 pb-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Your Profile</h1>
            <p className="text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>
          
          <div className="flex justify-center">
            <UserProfile 
              routing="path"
              path="/profile"
              appearance={{
                elements: {
                  rootBox: "mx-auto w-full max-w-4xl",
                  card: "shadow-lg border border-border bg-card",
                  navbar: "bg-muted/30 border-r border-border",
                  navbarButton: "text-foreground hover:bg-muted transition-colors",
                  navbarButtonActive: "bg-primary/10 text-primary",
                  pageScrollBox: "bg-card",
                  page: "bg-card",
                  profileSectionTitle: "text-foreground font-semibold",
                  profileSectionTitleText: "text-foreground",
                  profileSectionPrimaryButton: 
                    "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
                  formButtonPrimary: 
                    "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm transition-all",
                  formButtonReset: 
                    "text-muted-foreground hover:text-foreground transition-colors",
                  formFieldLabel: "text-foreground font-medium",
                  formFieldInput: 
                    "bg-background border-border text-foreground focus:ring-2 focus:ring-primary/50",
                  breadcrumbs: "text-muted-foreground",
                  breadcrumbsItem: "text-foreground hover:text-primary",
                  breadcrumbsItemDivider: "text-muted-foreground",
                  accordionTriggerButton: "text-foreground hover:bg-muted",
                  badge: "bg-primary/10 text-primary border-primary/20",
                  headerTitle: "text-foreground",
                  headerSubtitle: "text-muted-foreground",
                  menuButton: "text-foreground hover:bg-muted",
                  menuItem: "text-foreground hover:bg-muted",
                  avatarBox: "ring-2 ring-primary/20",
                  userButtonPopoverCard: "bg-card border-border shadow-lg",
                  userPreviewMainIdentifier: "text-foreground font-semibold",
                  userPreviewSecondaryIdentifier: "text-muted-foreground",
                  actionCard: "bg-muted/30 border-border",
                },
              }}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
