import { SignIn } from "@clerk/clerk-react";
import { Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/ui/theme-toggle";

const SignInPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">TransIntelliFlow</span>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 pb-12 flex items-center justify-center min-h-screen">
        <div className="w-full max-w-md mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
            <p className="text-muted-foreground">
              Sign in to access your fraud detection dashboard
            </p>
          </div>
          
          <SignIn 
            routing="path" 
            path="/sign-in"
            signUpUrl="/sign-up"
            afterSignInUrl="/dashboard"
            appearance={{
              elements: {
                rootBox: "mx-auto",
                card: "shadow-lg border border-border bg-card",
                headerTitle: "text-foreground",
                headerSubtitle: "text-muted-foreground",
                formButtonPrimary: 
                  "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm transition-all",
                formFieldLabel: "text-foreground font-medium",
                formFieldInput: 
                  "bg-background border-border text-foreground focus:ring-2 focus:ring-primary/50",
                footerActionLink: "text-primary hover:text-primary/80 font-medium",
                footerActionText: "text-foreground",
                footer: "hidden",
                footerAction: "hidden",
                identityPreviewEditButton: "text-primary",
                socialButtonsBlockButton: 
                  "bg-background border border-border text-foreground hover:bg-muted transition-colors",
                socialButtonsBlockButtonText: "text-foreground font-medium",
                dividerLine: "bg-border",
                dividerText: "text-muted-foreground",
                formFieldInputShowPasswordButton: "text-muted-foreground hover:text-foreground",
                otpCodeFieldInput: "border-border text-foreground",
                formResendCodeLink: "text-primary hover:text-primary/80",
                alert: "bg-destructive/10 border-destructive/20 text-destructive",
                alertText: "text-destructive",
              },
            }}
          />
          
          
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link to="/sign-up" className="text-primary hover:underline font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SignInPage;
