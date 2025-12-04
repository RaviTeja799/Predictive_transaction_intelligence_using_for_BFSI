import { ClerkProvider, ClerkLoaded, ClerkLoading } from "@clerk/clerk-react";
import { ReactNode } from "react";
import { useNavigate } from "react-router-dom";

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  console.warn(
    "Missing Clerk Publishable Key. Please add VITE_CLERK_PUBLISHABLE_KEY to your .env file.\n" +
    "Get your key from https://dashboard.clerk.com"
  );
}

interface ClerkProviderWithRoutesProps {
  children: ReactNode;
}

// Loading spinner component
const LoadingSpinner = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="text-center space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
      <p className="text-muted-foreground">Loading authentication...</p>
    </div>
  </div>
);

export const ClerkProviderWithRoutes = ({ children }: ClerkProviderWithRoutesProps) => {
  const navigate = useNavigate();

  if (!PUBLISHABLE_KEY) {
    // If no key, render children without Clerk (development fallback)
    return <>{children}</>;
  }

  return (
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      navigate={(to) => navigate(to)}
      appearance={{
        baseTheme: undefined,
        variables: {
          colorPrimary: "hsl(221, 83%, 53%)",
          colorBackground: "hsl(var(--background))",
          colorText: "hsl(var(--foreground))",
          colorTextSecondary: "hsl(var(--muted-foreground))",
          colorInputBackground: "hsl(var(--input))",
          colorInputText: "hsl(var(--foreground))",
          borderRadius: "0.75rem",
          fontFamily: "inherit",
        },
        elements: {
          formButtonPrimary: 
            "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm",
          card: "bg-card border border-border shadow-lg",
          headerTitle: "text-foreground font-bold",
          headerSubtitle: "text-muted-foreground",
          socialButtonsBlockButton: 
            "bg-background border border-border text-foreground hover:bg-muted",
          formFieldLabel: "text-foreground",
          formFieldInput: 
            "bg-input border border-border text-foreground focus:ring-2 focus:ring-primary",
          footerActionLink: "text-primary hover:text-primary/80",
          identityPreview: "bg-muted",
          identityPreviewText: "text-foreground",
          identityPreviewEditButton: "text-primary",
          userButtonPopoverCard: "bg-card border border-border",
          userButtonPopoverActionButton: "text-foreground hover:bg-muted",
          userButtonPopoverActionButtonText: "text-foreground",
          userButtonPopoverFooter: "hidden",
          userPreviewMainIdentifier: "text-foreground font-medium",
          userPreviewSecondaryIdentifier: "text-muted-foreground",
          avatarBox: "border-2 border-primary/20",
          badge: "bg-primary text-primary-foreground",
          menuButton: "text-foreground hover:bg-muted",
          menuList: "bg-card border border-border",
          menuItem: "text-foreground hover:bg-muted",
          navbar: "bg-card border-b border-border",
          navbarButton: "text-foreground hover:bg-muted",
          pageScrollBox: "bg-background",
          profileSection: "bg-card border border-border rounded-lg",
          profileSectionTitle: "text-foreground font-semibold",
          profileSectionContent: "text-muted-foreground",
          formFieldSuccessText: "text-green-600",
          formFieldErrorText: "text-destructive",
          alertText: "text-foreground",
          alertTextDanger: "text-destructive",
        },
      }}
      afterSignOutUrl="/"
    >
      <ClerkLoading>
        <LoadingSpinner />
      </ClerkLoading>
      <ClerkLoaded>
        {children}
      </ClerkLoaded>
    </ClerkProvider>
  );
};

export default ClerkProviderWithRoutes;
