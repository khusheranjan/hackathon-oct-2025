import { useNavigate } from "react-router-dom";
import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { Video } from "lucide-react";
import { useAuth } from "../context/authContext";
import { useState } from "react";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_URL || "";

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/google`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: credentialResponse.credential,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Authentication failed");
      }

      const data = await response.json();

      // Store token and user data
      login(data.token, data.user);

      // Redirect to chat interface
      navigate("/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError("Google Sign-In failed. Please try again.");
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Video className="h-12 w-12 text-primary" />
            <span className="text-3xl font-bold">EduVideo AI</span>
          </div>
          <h1 className="text-2xl font-semibold mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">
            Sign in to start creating amazing educational videos
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-card border border-border rounded-lg shadow-lg p-8">
          <h2 className="text-xl font-semibold mb-6 text-center">
            Sign in with Google
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-center">
            {isLoading ? (
              <div className="text-center py-4">
                <p className="text-muted-foreground">Signing in...</p>
              </div>
            ) : (
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap
                theme="outline"
                size="large"
                text="signin_with"
              />
            )}
          </div>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>

        {/* Back to Home */}
        <p className="mt-6 text-center text-sm">
          <a
            href="/"
            className="text-primary hover:underline"
          >
            Back to Home
          </a>
        </p>
      </div>
    </div>
  );
}
