import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

import {
  Settings,
  LogOut,
  AlertOctagon,
  Pill,
  CalendarCheck,
  Lock,
  PhoneCall,
  Stethoscope,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

// SOS can be sms or a call.

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const firstName = "John";

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
  ];

  const [sosOpen, setSosOpen] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const [alertSent, setAlertSent] = useState(false);
  
  const [user, setUser] = useState<{ name: string; dob: string; gender: string; phone: string; id: number } | null>(null);

  const isDark = document.documentElement.classList.contains("dark");

  useEffect(() => {
  const fetchUser = async () => {
    try {
      const response = await fetch("/api/v1/auth/me", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Important if backend sets HttpOnly cookies
      });

      if (!response.ok) {
        throw new Error("User not authenticated");
      }

      const data = await response.json();
        setUser(data);
      } catch (err) {
        console.error("Auth error:", err);
        navigate("/authentication"); // Redirect to authentication page if not authenticated
      }
    };

    fetchUser();
  }, []);


  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (sosOpen) {
      setCountdown(10);
      setAlertSent(false);
      timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            setAlertSent(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [sosOpen]);

  const handleClose = () => {
    setSosOpen(false);
    setAlertSent(false);
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col">
      <header className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Welcome, {user?.name}</h2>
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            className="hover:cursor-pointer"
            onClick={() => navigate("/settings")}
          >
            <Settings size={24} />
          </Button>
          <Button
            variant="ghost"
            className="hover:cursor-pointer"
            onClick={() => navigate("/authentication")}
          >
            <LogOut size={24} />
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-4 flex-grow">
        {menuItems.map((item) => (
          <Card
            key={item.title}
            className="cursor-pointer flex flex-col items-center justify-center active:bg-zinc-100 hover:bg-zinc-100 dark:active:bg-zinc-900/20 dark:hover:bg-zinc-900/50"
            onClick={() => navigate(item.route)}
          >
            <CardHeader className="flex flex-col items-center">
              <item.icon size={30} />
            </CardHeader>
            <CardTitle className="text-center text-sm">{item.title}</CardTitle>
          </Card>
        ))}
      </div>

      <div className="mt-6 w-full">
        <Button
          variant="destructive"
          className="w-full flex items-center justify-center hover:cursor-pointer"
          onClick={() => setSosOpen(true)}
        >
          <AlertOctagon size={20} className="" /> SOS
        </Button>
      </div>

      <Dialog open={sosOpen} onOpenChange={handleClose}>
        <DialogContent className="w-[300px] h-[300px] rounded-xl flex flex-col items-center justify-center p-4">
          <DialogHeader className="text-center">
            <DialogTitle className="text-lg font-semibold mb-1">
              {alertSent ? "Alert Sent!" : "Sending Alert"}
            </DialogTitle>

            {!alertSent && (
              <div className="w-28 h-28 mx-auto my-2">
                <CircularProgressbar
                  value={(countdown / 10) * 100}
                  text={`${countdown}s`}
                  strokeWidth={10}
                  styles={buildStyles({
                    pathColor: isDark ? "white" : "black",
                    trailColor: "transparent",
                    textColor: isDark ? "white" : "black",
                    textSize: "18px",
                    strokeLinecap: "round",
                    pathTransitionDuration: 0.3,
                  })}
                />
              </div>
            )}

            <DialogDescription className="text-sm text-center">
              {alertSent
                ? "Your emergency contacts have been notified."
                : `Alert will be sent in ${countdown} seconds.`}
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="justify-center mt-4">
            <Button variant="outline" onClick={handleClose}>
              {alertSent ? "Close" : "Cancel"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default HomePage;
