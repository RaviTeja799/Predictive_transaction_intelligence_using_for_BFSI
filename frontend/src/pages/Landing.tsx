import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Shield,
  TrendingUp,
  Zap,
  BarChart3,
  Lock,
  Database,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";
import { Link } from "react-router-dom";

const Landing = () => {
  const features = [
    {
      icon: Shield,
      title: "Advanced Fraud Detection",
      description:
        "AI-powered algorithms detect suspicious patterns in real-time, protecting your financial ecosystem.",
    },
    {
      icon: BarChart3,
      title: "Comprehensive Analytics",
      description:
        "Interactive dashboards with deep insights into transaction patterns, fraud trends, and risk analysis.",
    },
    {
      icon: Zap,
      title: "Real-time Monitoring",
      description:
        "Instant alerts and continuous monitoring of all transactions across multiple channels.",
    },
    {
      icon: TrendingUp,
      title: "Predictive Intelligence",
      description:
        "Machine learning models predict and prevent fraud before it happens with 95%+ accuracy.",
    },
    {
      icon: Lock,
      title: "Secure & Compliant",
      description:
        "Bank-grade security with full compliance to RBI, PCI-DSS, and international standards.",
    },
    {
      icon: Database,
      title: "Big Data Processing",
      description:
        "Process millions of transactions efficiently with scalable infrastructure.",
    },
  ];

  const stats = [
    { value: "95.34%", label: "Detection Accuracy" },
    { value: "5000+", label: "Transactions Analyzed" },
    { value: "<100ms", label: "Response Time" },
    { value: "24/7", label: "Monitoring" },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-accent/5">
        <div className="container mx-auto px-4 py-20 lg:py-32">
          <div className="flex flex-col items-center text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium">
              <Shield className="h-4 w-4" />
              Advanced BFSI Fraud Detection
            </div>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight max-w-4xl">
              Predictive Transaction
              <span className="block text-primary mt-2">Intelligence Platform</span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl">
              Protect your financial institution with AI-powered fraud detection.
              Real-time monitoring, predictive analytics, and comprehensive insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button size="lg" asChild className="text-lg h-12 px-8">
                <Link to="/login">
                  Access Console
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="text-lg h-12 px-8">
                <Link to="/predict">
                  Test Fraud Detection
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
      </section>

      {/* Stats Section */}
      <section className="py-12 border-y bg-card/50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Comprehensive Fraud Protection
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to detect, prevent, and analyze fraudulent transactions
              in your banking ecosystem.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="transition-all hover:shadow-lg">
                <CardContent className="p-6 space-y-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 lg:py-32 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our intelligent system analyzes transactions in real-time using advanced
              machine learning algorithms.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Data Collection",
                description:
                  "Aggregate transaction data from multiple channels including mobile, web, ATM, and POS systems.",
              },
              {
                step: "02",
                title: "AI Analysis",
                description:
                  "Machine learning models analyze patterns, behavioral anomalies, and risk indicators in real-time.",
              },
              {
                step: "03",
                title: "Actionable Insights",
                description:
                  "Get instant alerts, comprehensive reports, and predictive analytics to prevent fraud.",
              },
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="text-6xl font-bold text-primary/10 mb-4">{item.step}</div>
                <h3 className="text-2xl font-semibold mb-3">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
                <div className="flex items-center gap-2 mt-4 text-primary">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="text-sm font-medium">Automated & Efficient</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4">
          <Card className="bg-gradient-to-br from-primary to-primary-glow text-primary-foreground">
            <CardContent className="p-12 text-center space-y-6">
              <h2 className="text-3xl md:text-5xl font-bold">
                Ready to Protect Your Institution?
              </h2>
              <p className="text-xl opacity-90 max-w-2xl mx-auto">
                Start analyzing your transaction data with our powerful fraud detection
                platform today.
              </p>
              <div className="pt-4 flex gap-4 justify-center">
                <Button
                  size="lg"
                  variant="secondary"
                  asChild
                  className="text-lg h-12 px-8"
                >
                  <Link to="/login">
                    View Live Dashboard
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  asChild
                  className="text-lg h-12 px-8 bg-white/10 hover:bg-white/20"
                >
                  <Link to="/predict">
                    Try Prediction
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Shield className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold">PTI System</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Advanced predictive transaction intelligence for BFSI institutions.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/login" className="hover:text-primary transition-colors">Dashboard</Link></li>
                <li><Link to="/predict" className="hover:text-primary transition-colors">Fraud Prediction</Link></li>
                <li><a href="#features" className="hover:text-primary transition-colors">Features</a></li>
                <li><a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">API Docs</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Team</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>Team Predictive Intelligence</li>
                <li>BFSI Fraud Detection</li>
                <li>Milestone 1: Data Visualization</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t pt-8 text-center text-sm text-muted-foreground">
            <p>© 2025 Predictive Transaction Intelligence. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
