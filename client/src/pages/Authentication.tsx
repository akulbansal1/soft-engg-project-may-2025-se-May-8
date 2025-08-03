import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import {
  CalendarIcon,
  User,
  Phone,
  ScanFace,
  UserCheck2Icon,
  UserPlus2,
} from "lucide-react";
import { format } from "date-fns";
import * as yup from "yup";
import { useNavigate } from "react-router-dom";
import BackgroundAnimation from "@/components/BackgroundAnimation";

// ✅ Yup Schemas

const phoneValidation = yup
  .string()
  .required("Phone number is required")
  .matches(/^\+?\d+$/, "Phone number must contain only digits");

export const signInSchema = yup.object({
  phone: phoneValidation,
});

export const signupSchema = yup.object({
  firstName: yup.string().required("First name is required"),
  lastName: yup.string().required("Last name is required"),
  phone: phoneValidation,
  dob: yup.string().required("Date of birth is required"),
  gender: yup.string().required("Gender is required"),
});

const AuthenticationPage: React.FC = () => {
  const navigate = useNavigate();
  const [date, setDate] = React.useState<Date>();
  const [signInPhone, setSignInPhone] = React.useState("");
  const [signInError, setSignInError] = React.useState("");

  const [signupData, setSignupData] = React.useState({
    firstName: "",
    lastName: "",
    phone: "",
    dob: "",
    gender: "",
  });
  const [signupErrors, setSignupErrors] = React.useState<{
    [key: string]: string;
  }>({});
  const [loading, setLoading] = React.useState(false);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSignupErrors({});
    if (!signupData.firstName) {
      setSignupErrors((prev) => ({
        ...prev,
        firstName: "First name is required",
      }));
    }
    if (!signupData.lastName) {
      setSignupErrors((prev) => ({
        ...prev,
        lastName: "Last name is required",
      }));
    }
    if (!signupData.phone) {
      setSignupErrors((prev) => ({
        ...prev,
        phone: "Phone number is required",
      }));
    }
    if (!signupData.dob) {
      setSignupErrors((prev) => ({
        ...prev,
        dob: "Date of birth is required",
      }));
    }
    if (!signupData.gender) {
      setSignupErrors((prev) => ({
        ...prev,
        gender: "Gender is required",
      }));
    }

    if (!signupData.firstName || !signupData.lastName || !signupData.phone || !signupData.dob || !signupData.gender) {
      setLoading(false);
      return;
    }

    try {
      // Send POST request to backend API
      const response = await fetch("/api/v1/auth/sms/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phone: signupData.phone }), // Include '+' if not already present
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to send OTP.");
      }

      navigate("/otp", { state: { user_info: signupData } });

    } catch (err: any) {
      if (err.name === "ValidationError" && err.errors?.[0]) {
        setSignupErrors(err.errors[0]);
      } else {
        setSignupErrors(err.message || "An unexpected error occurred.");
      }
      console.log("OTP API error:", err);
    } finally {
      setLoading(false);
    }
    
  };



  const handleSignInChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSignInPhone(e.target.value);
    if (signInError) setSignInError("");
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSignupData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    if (signupErrors[e.target.name]) {
      setSignupErrors((prev) => ({ ...prev, [e.target.name]: "" }));
    }
  };

  const handleGenderChange = (value: string) => {
    setSignupData((prev) => ({ ...prev, gender: value }));
    if (signupErrors.gender) {
      setSignupErrors((prev) => ({ ...prev, gender: "" }));
    }
  };

  return (
    <div className="relative min-h-[calc(100dvh-110px)] flex items-center justify-center p-4 overflow-hidden">
      <BackgroundAnimation />

      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            Welcome Back
          </h1>
          <p className="text-muted-foreground">
            Sign in to your Svaasthy account or create a new one
          </p>
        </div>

        <div className="relative">
          <div className="p-8 rounded-3xl bg-card/80 backdrop-blur-sm border border-border shadow-xl">
            <Tabs defaultValue="signin" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger
                  value="signin"
                  className="data-[state=active]:bg-background data-[state=active]:text-foreground"
                >
                  <UserCheck2Icon className="w-4 h-4 mr-2" /> Sign In
                </TabsTrigger>
                <TabsTrigger
                  value="signup"
                  className="data-[state=active]:bg-background data-[state=active]:text-foreground"
                >
                  <UserPlus2 className="w-4 h-4 mr-2" /> Sign Up
                </TabsTrigger>
              </TabsList>

              {/* Sign In */}
              <TabsContent value="signin" className="space-y-6">
                <form onSubmit={handleSignIn}>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      type="tel"
                      name="phone"
                      placeholder="Phone Number"
                      value={signInPhone}
                      onChange={handleSignInChange}
                      className="pl-10 h-12 rounded-xl"
                    />
                  </div>
                  {signInError && (
                    <p className="text-red-500 text-xs mt-1">{signInError}</p>
                  )}

                  <div className="flex flex-col mt-5">
                    <Button
                      type="button"
                      className="flex-1 h-12 rounded-xl"
                      onClick={() => navigate("/face-id")}
                    >
                      <ScanFace className="w-4 h-4 mr-2" />Login with Face ID
                    </Button>
                  </div>
                </form>
              </TabsContent>

              {/* Sign Up */}
              <TabsContent value="signup" className="space-y-6">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Input
                        type="text"
                        name="firstName"
                        placeholder="First Name"
                        value={signupData.firstName}
                        onChange={handleChange}
                        className="h-12 rounded-xl"
                      />
                      {signupErrors.firstName && (
                        <p className="text-red-500 text-xs mt-1">
                          {signupErrors.firstName}
                        </p>
                      )}
                    </div>
                    <div>
                      <Input
                        type="text"
                        name="lastName"
                        placeholder="Last Name"
                        value={signupData.lastName}
                        onChange={handleChange}
                        className="h-12 rounded-xl"
                      />
                      {signupErrors.lastName && (
                        <p className="text-red-500 text-xs mt-1">
                          {signupErrors.lastName}
                        </p>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        type="tel"
                        name="phone"
                        placeholder="Phone Number"
                        value={signupData.phone}
                        onChange={handleChange}
                        className="pl-10 h-12 rounded-xl"
                      />
                    </div>
                    {signupErrors.phone && (
                      <p className="text-red-500 text-xs mt-1">
                        {signupErrors.phone}
                      </p>
                    )}
                  </div>

                  <div>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          data-empty={!date}
                          className="data-[empty=true]:text-muted-foreground flex items-center gap-2 w-full justify-start text-left font-normal h-12 rounded-xl"
                        >
                          <CalendarIcon className="w-4 h-4" />
                          {date ? (
                            format(date, "yyyy-MM-dd")
                          ) : (
                            <span>Select Date of Birth</span>
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={date}
                          onSelect={(d) => {
                            setDate(d);
                            setSignupData((prev) => ({
                              ...prev,
                              dob: d ? d.toISOString().split("T")[0] : "",
                            }));
                            if (signupErrors.dob)
                              setSignupErrors((prev) => ({
                                ...prev,
                                dob: "",
                              }));
                          }}
                          captionLayout="dropdown"
                        />
                      </PopoverContent>
                    </Popover>
                    {signupErrors.dob && (
                      <p className="text-red-500 text-xs mt-1">
                        {signupErrors.dob}
                      </p>
                    )}
                  </div>

                  <div>
                    <Select
                      onValueChange={handleGenderChange}
                      value={signupData.gender}
                    >
                      <SelectTrigger className="w-full h-12 rounded-xl">
                        <SelectValue placeholder="Select Gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Male">Male</SelectItem>
                        <SelectItem value="Female">Female</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                        <SelectItem value="prefer_not_say">
                          Prefer not to say
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    {signupErrors.gender && (
                      <p className="text-red-500 text-xs mt-1">
                        {signupErrors.gender}
                      </p>
                    )}
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 rounded-xl"
                    disabled={loading}
                  >
                    <User className="w-4 h-4 mr-2" />
                    {loading ? "Creating Account..." : "Create Account"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthenticationPage;
