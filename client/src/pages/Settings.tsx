import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Calendar, Phone, ArrowLeft, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";

// Define the structure of the user data we expect from the API
interface UserProfile {
  id: number;
  name: string;
  phone: string;
  dob: string;
  gender: string;
}

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [userInfo, setUserInfo] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      setIsLoading(true);
      fetch(`/api/v1/users/${user.id}`)
        .then((res) => {
          if (!res.ok) {
            throw new Error("Failed to fetch user profile");
          }
          return res.json();
        })
        .then((data: UserProfile) => {
          setUserInfo(data);
        })
        .catch((err) => {
          console.error("Error fetching user profile:", err);
          toast.error("Could not load your profile information.");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [user]);

  const calculateAge = (dob: string) => {
    if (!dob) return "";
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age.toString();
  };

  const getInitials = (name: string) => {
    if (!name) return "?";
    const names = name.split(" ");
    const firstName = names[0]?.[0] || "";
    const lastName = names.length > 1 ? names[names.length - 1]?.[0] : "";
    return `${firstName}${lastName}`.toUpperCase();
  };

  const InfoField = ({
    label,
    value,
    icon: Icon,
  }: {
    label: string;
    value: string;
    icon: React.ElementType;
  }) => (
    <div className="flex items-center space-x-4 p-4 rounded-lg bg-secondary/50 border">
      <Icon size={20} className="text-primary flex-shrink-0" />
      <div>
        <p className="text-sm text-foreground/80">{label}</p>
        <p className="font-semibold text-foreground text-base">
          {value || "Not set"}
        </p>
      </div>
    </div>
  );

  const SkeletonLoader = () => (
    <div className="space-y-6">
      {[...Array(2)].map((_, cardIndex) => (
        <Card key={cardIndex} className="animate-pulse">
          <CardHeader className="pb-3">
            <div className="h-6 w-48 bg-muted rounded"></div>
          </CardHeader>
          <CardContent className="space-y-4">
            {[...Array(2)].map((_, fieldIndex) => (
              <div
                key={fieldIndex}
                className="flex items-center space-x-4 p-4 rounded-lg bg-background border"
              >
                <div className="h-5 w-5 bg-muted rounded-full"></div>
                <div>
                  <div className="h-4 w-20 bg-muted rounded mb-2"></div>
                  <div className="h-5 w-32 bg-muted rounded"></div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div>
      <div className="mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-md"
              onClick={() => navigate("/home")}
            >
              <ArrowLeft size={20} />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Settings</h1>
              <p className="text-sm text-foreground/70">
                Manage your profile and privacy
              </p>
            </div>
          </div>
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary to-primary/80 flex items-center justify-center font-bold text-lg text-primary-foreground">
            {userInfo ? getInitials(userInfo.name) : <User size={24} />}
          </div>
        </div>

        {isLoading ? (
          <SkeletonLoader />
        ) : !userInfo ? (
          <Card>
            <CardContent className="pt-6 text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
              <h3 className="mt-4 text-lg font-medium">
                Could not load profile
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Please try refreshing the page.
              </p>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Personal Information Card */}
            <Card className="bg-transparent">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-3">
                  <User size={20} className="text-foreground/80" />
                  <span>Personal Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <InfoField
                  label="Full Name"
                  value={userInfo.name}
                  icon={User}
                />
                <InfoField
                  label="Age"
                  value={calculateAge(userInfo.dob)}
                  icon={Calendar}
                />
              </CardContent>
            </Card>

            {/* Contact Information Card */}
            <Card className="bg-transparent">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-3">
                  <Phone size={20} className="text-foreground/80" />
                  <span>Contact Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <InfoField
                  label="Phone Number"
                  value={userInfo.phone}
                  icon={Phone}
                />
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default Settings;
