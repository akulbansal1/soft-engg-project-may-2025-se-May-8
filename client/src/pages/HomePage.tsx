import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import {
  Settings,
  LogOut,
  AlertTriangle,
  Pill,
  CalendarCheck,
  Lock,
  PhoneCall,
  Stethoscope,
  User,
} from "lucide-react";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading, logout } = useAuth();

  const menuItems = [
    { title: "Medicines", route: "/medicines", icon: Pill },
    { title: "Appointments", route: "/appointments", icon: CalendarCheck },
    { title: "Data Vault", route: "/data-vault", icon: Lock },
    {
      title: "Emergency Contacts",
      route: "/emergency-contacts",
      icon: PhoneCall,
    },
    { title: "Book a Doctor", route: "/book-doctor", icon: Stethoscope },
    { title: "Settings", route: "/settings", icon: Settings },
  ];

  const [sosOpen, setSosOpen] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const [alertSent, setAlertSent] = useState(false);
  const [theme, setTheme] = useState("light");

  // Detect the current theme for the progress bar text color
  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");
  }, []);

  // Countdown logic for the SOS alert
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (sosOpen && !alertSent) {
      timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            triggerSOS();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [sosOpen, alertSent]);

  const triggerSOS = async () => {
    if (!user) return;
    try {
      console.log("SOS Triggered for user:", user.id);
      setAlertSent(true);
      toast.info("SOS alert has been sent to your emergency contacts.");
    } catch (error) {
      console.error("Failed to trigger SOS:", error);
      toast.error("Could not send SOS alert. Please try again.");
      handleCloseSos();
    }
  };

  const handleOpenSos = () => {
    setCountdown(10);
    setAlertSent(false);
    setSosOpen(true);
  };

  const handleCloseSos = () => setSosOpen(false);
  const handleLogout = async () => {
    await logout();
    navigate("/authentication");
  };

  const getInitials = (name: string) => {
    if (!name) return "?";
    const names = name.split(" ");
    const firstName = names[0]?.[0] || "";
    const lastName = names.length > 1 ? names[names.length - 1]?.[0] : "";
    return `${firstName}${lastName}`.toUpperCase();
  };

  const SkeletonLoader = () => (
    <div className="animate-pulse">
      <header className="flex justify-between items-center mb-8">
        <div className="space-y-2">
          <div className="h-7 w-48 bg-muted rounded-md"></div>
          <div className="h-5 w-32 bg-muted rounded-md"></div>
        </div>
        <div className="h-12 w-12 bg-muted rounded-full"></div>
      </header>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Card
            key={i}
            className="flex flex-col items-center justify-center p-4 h-32"
          >
            <div className="h-8 w-8 bg-muted rounded-full mb-2"></div>
            <div className="h-5 w-20 bg-muted rounded-md"></div>
          </Card>
        ))}
      </div>
      <div className="mt-6 w-full">
        <Button disabled className="w-full h-16 bg-muted"></Button>
      </div>
    </div>
  );

  if (isLoading) {
    return <SkeletonLoader />;
  }

  return (
    <TooltipProvider>
      <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col">
        <header className="flex justify-between items-center mb-8">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold text-foreground">
              Welcome, {user?.name.split(" ")[0]}
            </h1>
            <p className="text-muted-foreground">
              Your personal health dashboard.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={handleLogout}>
                  <LogOut className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Logout</p>
              </TooltipContent>
            </Tooltip>
            <Avatar>
              <AvatarFallback className="font-bold">
                {user ? getInitials(user.name) : <User />}
              </AvatarFallback>
            </Avatar>
          </div>
        </header>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 flex-grow">
          {menuItems.map((item) => (
            <Card
              key={item.title}
              className="cursor-pointer flex flex-col items-center justify-center text-center p-4 hover:bg-secondary/50 hover:shadow-lg active:scale-95"
              onClick={() => navigate(item.route)}
            >
              <item.icon className="h-8 w-8 mb-2 text-primary" />
              <CardTitle className="text-sm font-semibold">
                {item.title}
              </CardTitle>
            </Card>
          ))}
        </div>

        <div className="mt-6 w-full">
          <Card className="bg-destructive/10 border-destructive/30">
            <CardContent className="p-4 flex flex-col sm:flex-row items-center justify-between">
              <div className="flex items-center gap-4 mb-4 sm:mb-0">
                <AlertTriangle className="h-8 w-8 text-destructive" />
                <div>
                  <h3 className="font-bold text-destructive">Emergency SOS</h3>
                  <p className="text-sm text-destructive/80">
                    Alert your contacts immediately.
                  </p>
                </div>
              </div>
              <Button
                variant="destructive"
                className="w-full sm:w-auto"
                onClick={handleOpenSos}
              >
                Trigger SOS
              </Button>
            </CardContent>
          </Card>
        </div>

        <AlertDialog open={sosOpen} onOpenChange={setSosOpen}>
          <AlertDialogContent className="w-[320px] rounded-2xl">
            <AlertDialogHeader className="text-center">
              <AlertDialogTitle className="text-2xl font-bold">
                {alertSent ? "Alert Sent!" : "Sending SOS"}
              </AlertDialogTitle>
              <div className="w-32 h-32 mx-auto my-4">
                <CircularProgressbar
                  value={alertSent ? 100 : (countdown / 10) * 100}
                  text={!alertSent ? `${countdown}s` : `✓`}
                  strokeWidth={8}
                  styles={buildStyles({
                    pathColor: alertSent
                      ? `hsl(var(--primary))`
                      : `hsl(var(--destructive))`,
                    trailColor: "hsl(var(--muted))",
                    textColor: "gray",
                    textSize: alertSent ? "32px" : "24px",
                    pathTransitionDuration: 0.5,
                  })}
                />
              </div>
              <AlertDialogDescription>
                {alertSent
                  ? "Your emergency contacts and location have been notified."
                  : "An alert will be sent unless you cancel."}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={handleCloseSos} className="w-full">
                {alertSent ? "Close" : "Cancel"}
              </AlertDialogCancel>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </TooltipProvider>
  );
};

export default HomePage;
