import { Moon, Sun, Trash2, LogOut, Video, Menu, Crown } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../../context/themeContext";
import { useAuth } from "../../context/authContext";
import { Button } from "../ui/button";
import { useEffect, useState } from "react";

interface HeaderProps {
  onClearChat: () => void;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function Header({
  onClearChat,
  isSidebarOpen: _isSidebarOpen,
  onToggleSidebar,
}: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<any>(null);

  const API_URL = import.meta.env.VITE_URL || "http://localhost:5000";

  useEffect(() => {
    if (token) {
      fetchSubscription();
    }
  }, [token]);

  const fetchSubscription = async () => {
    try {
      const response = await fetch(`${API_URL}/api/subscription/status`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setSubscription(data.subscription);
      }
    } catch (error) {
      console.error("Error fetching subscription:", error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="border-b border-border bg-background">
      <div className="px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSidebar}
            title="Toggle sidebar"
            className="hover:bg-accent"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <Video className="w-6 h-6 text-primary" />
          <h1 className="text-lg font-semibold">EduVideo AI</h1>
        </div>

        <div className="flex items-center gap-2">
          {subscription && (
            <Button
              variant="ghost"
              onClick={() => navigate("/pricing")}
              className="hidden sm:flex items-center gap-2"
            >
              {subscription.tier === "pro" ? (
                <>
                  <Crown className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">Pro</span>
                </>
              ) : (
                <span className="text-sm text-muted-foreground">Free Plan</span>
              )}
              <span className="text-xs text-muted-foreground">
                ({subscription.usage.videos_generated}/{subscription.tier === "free" ? "1" : "50"})
              </span>
            </Button>
          )}
          {user && (
            <div className="hidden sm:flex items-center gap-2 mr-2">
              {user.picture && (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
              )}
              <span className="text-sm text-muted-foreground">
                {user.name}
              </span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onClearChat}
            title="Clear conversation"
            className="hover:bg-accent"
          >
            <Trash2 className="w-5 h-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            className="hover:bg-accent"
          >
            {theme === "light" ? (
              <Moon className="w-5 h-5" />
            ) : (
              <Sun className="w-5 h-5" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Logout"
            className="hover:bg-accent"
          >
            <LogOut className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
