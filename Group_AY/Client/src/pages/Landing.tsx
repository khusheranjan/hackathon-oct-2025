import { Link } from "react-router-dom";
import { Video, Sparkles, Zap, Users } from "lucide-react";
import { Button } from "../components/ui/button";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Video className="h-8 w-8 text-primary" />
          <span className="text-2xl font-bold">EduVideo AI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/pricing">
            <Button variant="ghost">Pricing</Button>
          </Link>
          <Link to="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-600">
          Create Educational Videos
          <br />
          with AI Magic
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Transform your ideas into engaging educational videos with the power
          of AI. Generate scripts, voiceovers, and visuals in minutes.
        </p>
        <Link to="/login">
          <Button className="text-lg px-8 py-6">
            Get Started Free
          </Button>
        </Link>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Why Choose EduVideo AI?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Sparkles className="h-10 w-10 text-primary" />}
            title="AI-Powered Generation"
            description="Leverage cutting-edge AI to generate compelling educational content from simple descriptions."
          />
          <FeatureCard
            icon={<Zap className="h-10 w-10 text-primary" />}
            title="Lightning Fast"
            description="Create professional-quality videos in minutes, not hours. Perfect for educators on the go."
          />
          <FeatureCard
            icon={<Users className="h-10 w-10 text-primary" />}
            title="Made for Educators"
            description="Built specifically for teachers, trainers, and content creators who want to engage learners."
          />
        </div>
      </section>

      {/* Pricing Teaser */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-8">
          Simple Pricing
        </h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-card p-8 rounded-lg border border-border">
            <h3 className="text-2xl font-bold mb-2">Free</h3>
            <p className="text-4xl font-bold mb-4">₹0</p>
            <p className="text-muted-foreground mb-4">
              Perfect to get started. Create 1 video up to 1 minute.
            </p>
            <Link to="/login">
              <Button className="w-full">Get Started Free</Button>
            </Link>
          </div>
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-8 rounded-lg text-white">
            <h3 className="text-2xl font-bold mb-2">Pro</h3>
            <p className="text-4xl font-bold mb-4">₹499<span className="text-lg">/mo</span></p>
            <p className="mb-4">
              Create 50 videos/month with avatars, advanced features & more.
            </p>
            <Link to="/pricing">
              <Button className="w-full bg-white text-blue-600 hover:bg-gray-100">
                View All Plans
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="bg-primary/10 rounded-lg p-12">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your Teaching?
          </h2>
          <p className="text-lg text-muted-foreground mb-6">
            Join thousands of educators creating amazing content with AI.
          </p>
          <Link to="/login">
            <Button className="text-lg px-8 py-6">
              Start Creating Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-muted-foreground">
        <p>&copy; 2025 EduVideo AI. All rights reserved.</p>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="bg-card p-6 rounded-lg border border-border hover:shadow-lg transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
