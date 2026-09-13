import { SignIn } from "@clerk/clerk-react";

const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-6">
      <SignIn 
        routing="path" 
        path="/login"
        signUpUrl="/signup"
        redirectUrl="/dashboard"
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-gradient-card border-border glow-primary",
            headerTitle: "text-foreground",
            headerSubtitle: "text-muted-foreground",
            socialButtonsBlockButton: "border-border hover:bg-accent",
            formButtonPrimary: "cta-button",
            footerActionLink: "text-primary hover:text-primary-glow",
            input: "bg-input border-border text-foreground",
            label: "text-foreground"
          }
        }}
      />
    </div>
  );
};

export default Login;