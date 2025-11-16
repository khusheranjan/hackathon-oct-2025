import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContext";
import { Check, Zap, Crown } from "lucide-react";

declare global {
  interface Window {
    Razorpay: any;
  }
}

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  billing_cycle?: string;
  discount?: string;
  features: {
    videos_per_month?: number;
    videos_per_account?: number;
    max_video_duration: number;
    avatar_enabled: boolean;
    advanced_features: boolean;
    watermark: boolean;
    priority_support?: boolean;
  };
}

interface CreditPackage {
  name: string;
  credits: number;
  price: number;
  currency: string;
  discount?: string;
}

const Pricing = () => {
  const navigate = useNavigate();
  const { isAuthenticated, token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [pricing, setPricing] = useState<{
    subscriptions: Record<string, PricingPlan>;
    credit_packages: Record<string, CreditPackage>;
  } | null>(null);
  const [subscription, setSubscription] = useState<any>(null);

  const API_URL = import.meta.env.VITE_URL || "http://localhost:5000";

  useEffect(() => {
    // Load Razorpay script
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);

    // Fetch pricing info
    fetchPricing();

    // Fetch user subscription if authenticated
    if (isAuthenticated && token) {
      fetchSubscription();
    }

    return () => {
      document.body.removeChild(script);
    };
  }, [isAuthenticated, token]);

  const fetchPricing = async () => {
    try {
      const response = await fetch(`${API_URL}/api/pricing`);
      const data = await response.json();
      if (data.success) {
        setPricing(data.pricing);
      }
    } catch (error) {
      console.error("Error fetching pricing:", error);
    }
  };

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

  const handleUpgrade = async (planId: string, type: "subscription" | "credits") => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    setLoading(true);

    try {
      // Create order
      const orderResponse = await fetch(`${API_URL}/api/payment/create-order`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          type: type,
          plan: planId,
        }),
      });

      const orderData = await orderResponse.json();

      if (!orderData.success) {
        alert(orderData.error || "Failed to create order");
        setLoading(false);
        return;
      }

      // Open Razorpay checkout
      const options = {
        key: orderData.razorpay_key,
        amount: orderData.order.amount * 100,
        currency: orderData.order.currency,
        order_id: orderData.order.id,
        name: "AI Video Generator",
        description: type === "subscription" ? "Subscription Payment" : "Credit Purchase",
        handler: async function (response: any) {
          // Verify payment
          try {
            const verifyResponse = await fetch(`${API_URL}/api/payment/verify`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_signature: response.razorpay_signature,
                transaction_id: orderData.order.transaction_id,
                type: type,
                plan: planId,
              }),
            });

            const verifyData = await verifyResponse.json();

            if (verifyData.success) {
              alert(verifyData.message);
              fetchSubscription();
              navigate("/chat");
            } else {
              alert(verifyData.error || "Payment verification failed");
            }
          } catch (error) {
            console.error("Payment verification error:", error);
            alert("Payment verification failed");
          } finally {
            setLoading(false);
          }
        },
        prefill: {
          name: user?.name || "",
          email: user?.email || "",
        },
        theme: {
          color: "#3B82F6",
        },
        modal: {
          ondismiss: function () {
            setLoading(false);
          },
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error) {
      console.error("Payment error:", error);
      alert("Failed to initiate payment");
      setLoading(false);
    }
  };

  if (!pricing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Choose the plan that works best for you. Start for free, upgrade anytime.
          </p>
        </div>

        {/* Current Subscription Status */}
        {subscription && (
          <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold mb-2">Your Current Plan</h3>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-2xl font-bold capitalize">{subscription.tier} Plan</p>
                <p className="text-gray-600 dark:text-gray-400">
                  Videos used: {subscription.usage.videos_generated} / {subscription.tier === "free" ? "1 (lifetime)" : "50 (monthly)"}
                </p>
                {subscription.credits > 0 && (
                  <p className="text-blue-600 font-medium">Additional Credits: {subscription.credits}</p>
                )}
              </div>
              {subscription.tier === "free" && (
                <button
                  onClick={() => handleUpgrade("pro_monthly", "subscription")}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  disabled={loading}
                >
                  Upgrade Now
                </button>
              )}
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {/* Free Plan */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border-2 border-gray-200 dark:border-gray-700">
            <div className="flex items-center mb-4">
              <Zap className="w-8 h-8 text-gray-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Free</h3>
            </div>
            <div className="mb-6">
              <span className="text-5xl font-bold text-gray-900 dark:text-white">₹0</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2">forever</span>
            </div>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300">1 video per account</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300">Max 1 minute duration</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300">Basic animations</span>
              </li>
              <li className="flex items-start text-gray-400 dark:text-gray-500">
                <span className="mr-3">✕</span>
                <span>Avatar feature</span>
              </li>
            </ul>
            <button
              onClick={() => navigate(isAuthenticated ? "/chat" : "/login")}
              className="w-full py-3 px-6 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition font-semibold"
            >
              {isAuthenticated ? "Go to Dashboard" : "Get Started Free"}
            </button>
          </div>

          {/* Pro Plan */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-2xl p-8 relative transform hover:scale-105 transition-transform">
            <div className="absolute top-0 right-0 bg-yellow-400 text-gray-900 px-4 py-1 rounded-bl-lg rounded-tr-lg font-bold text-sm">
              MOST POPULAR
            </div>
            <div className="flex items-center mb-4">
              <Crown className="w-8 h-8 text-yellow-300 mr-3" />
              <h3 className="text-2xl font-bold text-white">Pro</h3>
            </div>
            <div className="mb-6">
              <span className="text-5xl font-bold text-white">₹{pricing.subscriptions.pro_monthly.price}</span>
              <span className="text-blue-200 ml-2">/month</span>
            </div>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start">
                <Check className="w-5 h-5 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-white">50 videos per month</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-white">Up to 10 minutes per video</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-white">Avatar feature included</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-white">Advanced animations</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-yellow-300 mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-white">Priority support</span>
              </li>
            </ul>
            <button
              onClick={() => handleUpgrade("pro_monthly", "subscription")}
              disabled={loading || subscription?.tier === "pro"}
              className="w-full py-3 px-6 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Processing..." : subscription?.tier === "pro" ? "Current Plan" : "Upgrade to Pro"}
            </button>
            <p className="text-center text-blue-200 mt-4 text-sm">
              Yearly plan: ₹{pricing.subscriptions.pro_yearly.price}/year (Save 17%)
            </p>
          </div>
        </div>

        {/* Credit Packages */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Need More? Buy Additional Credits
          </h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {Object.entries(pricing.credit_packages).map(([key, pkg]) => (
              <div
                key={key}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition"
              >
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{pkg.name}</h4>
                <p className="text-3xl font-bold text-blue-600 mb-4">
                  ₹{pkg.price}
                </p>
                <p className="text-gray-600 dark:text-gray-400 mb-4">{pkg.credits} video credits</p>
                {pkg.discount && (
                  <p className="text-green-600 font-medium text-sm mb-4">{pkg.discount}</p>
                )}
                <button
                  onClick={() => handleUpgrade(key, "credits")}
                  disabled={loading || !isAuthenticated}
                  className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {!isAuthenticated ? "Login to Buy" : "Buy Credits"}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-12">
          <button
            onClick={() => navigate("/")}
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
