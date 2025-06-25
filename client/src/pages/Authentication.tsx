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
  Shield,
  Fingerprint,
  Lock,
  User,
  Phone,
  Heart,
  ScanFace,
} from "lucide-react";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";

const AuthenticationPage: React.FC = () => {
  // Your existing state and handlers would go here
  const navigate = useNavigate();
  const [date, setDate] = React.useState<Date>();
  const [signInPhone, setSignInPhone] = React.useState("");
  const [signupData, setSignupData] = React.useState({
    firstName: "",
    lastName: "",
    phone: "",
    dob: "",
    gender: "",
  });
  // combine first, middle and last an
  const [loading, setLoading] = React.useState(false);
  const [msg, setMsg] = React.useState("");

  // Your existing handlers would go here
  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle sign in logic
  };

  const handleSignUp = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle sign up logic
  };

  const handleSignInChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSignInPhone(e.target.value);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSignupData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleGenderChange = (value: string) => {
    setSignupData((prev) => ({
      ...prev,
      gender: value,
    }));
  };

  return (
    <div className="relative min-h-[calc(100dvh-110px)] flex items-center justify-center p-4 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute top-16 left-16 w-4 h-4 rounded-full bg-green-500/25 animate-bounce"
          style={{ animationDuration: "3.2s", animationDelay: "0s" }}
        />
        <div
          className="absolute top-28 right-24 w-3 h-3 rounded-full bg-blue-500/30 animate-bounce"
          style={{ animationDuration: "2.8s", animationDelay: "1.2s" }}
        />
        <div
          className="absolute top-48 left-8 w-5 h-5 rounded-full bg-purple-500/20 animate-bounce"
          style={{ animationDuration: "3.5s", animationDelay: "2.1s" }}
        />
        <div
          className="absolute bottom-32 right-16 w-4 h-4 rounded-full bg-pink-500/25 animate-bounce"
          style={{ animationDuration: "2.6s", animationDelay: "0.8s" }}
        />
        <div
          className="absolute bottom-48 left-24 w-3 h-3 rounded-full bg-cyan-500/35 animate-bounce"
          style={{ animationDuration: "3.8s", animationDelay: "1.5s" }}
        />
        <div
          className="absolute top-1/3 right-8 w-6 h-6 rounded-full bg-indigo-500/20 animate-bounce"
          style={{ animationDuration: "2.9s", animationDelay: "0.3s" }}
        />
        <div
          className="absolute bottom-1/3 left-12 w-4 h-4 rounded-full bg-emerald-500/28 animate-bounce"
          style={{ animationDuration: "3.1s", animationDelay: "1.8s" }}
        />

        {/* Geometric shapes */}
        <div
          className="absolute top-20 left-1/3 w-10 h-10 border border-primary/15 rounded-lg rotate-45 animate-spin"
          style={{ animationDuration: "25s" }}
        />
        <div
          className="absolute bottom-20 right-1/3 w-8 h-8 border border-blue-500/20 rounded-full animate-spin"
          style={{ animationDuration: "18s", animationDirection: "reverse" }}
        />
        <div
          className="absolute top-2/3 left-20 w-6 h-6 border border-purple-500/15 rotate-12 animate-spin"
          style={{ animationDuration: "22s", animationDirection: "reverse" }}
        />
        <div
          className="absolute bottom-2/3 right-20 w-12 h-12 border border-green-500/10 rounded-xl rotate-45 animate-spin"
          style={{ animationDuration: "20s" }}
        />

        {/* Security/Medical themed shapes */}
        <div className="absolute top-32 right-1/4">
          <div className="relative w-8 h-8 opacity-8">
            <Shield
              className="w-8 h-8 text-green-500/15 animate-pulse"
              style={{ animationDuration: "4s" }}
            />
          </div>
        </div>
        <div className="absolute bottom-40 left-1/4">
          <div className="relative w-6 h-6 opacity-12">
            <Lock
              className="w-6 h-6 text-blue-500/20 animate-pulse"
              style={{ animationDuration: "3.5s", animationDelay: "1s" }}
            />
          </div>
        </div>
        <div className="absolute top-1/2 left-8">
          <div className="relative w-7 h-7 opacity-10">
            <Fingerprint
              className="w-7 h-7 text-purple-500/18 animate-pulse"
              style={{ animationDuration: "5s", animationDelay: "2s" }}
            />
          </div>
        </div>
        <div className="absolute top-1/2 right-8">
          <div className="relative w-6 h-6 opacity-12">
            <Heart
              className="w-6 h-6 text-pink-500/20 animate-pulse"
              style={{ animationDuration: "3.8s", animationDelay: "0.5s" }}
            />
          </div>
        </div>

        {/* Medical cross shapes */}
        <div className="absolute top-1/4 left-12">
          <div className="relative w-6 h-6 opacity-12">
            <div className="absolute top-1.5 left-0 w-6 h-3 bg-green-500/15 rounded-sm" />
            <div className="absolute top-0 left-1.5 w-3 h-6 bg-green-500/15 rounded-sm" />
          </div>
        </div>
        <div className="absolute bottom-1/4 right-12">
          <div className="relative w-8 h-8 opacity-10">
            <div className="absolute top-2 left-0 w-8 h-4 bg-blue-500/12 rounded-sm" />
            <div className="absolute top-0 left-2 w-4 h-8 bg-blue-500/12 rounded-sm" />
          </div>
        </div>

        {/* Subtle grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `
                 linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                 linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
               `,
            backgroundSize: "40px 40px",
          }}
        />

        {/* Additional floating elements */}
        <div
          className="absolute top-1/6 right-1/6 w-3 h-3 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-full animate-bounce"
          style={{ animationDuration: "2.7s", animationDelay: "1.3s" }}
        />
        <div
          className="absolute bottom-1/6 left-1/6 w-5 h-5 bg-gradient-to-r from-teal-500/15 to-green-500/15 rounded-full animate-bounce"
          style={{ animationDuration: "3.3s", animationDelay: "0.7s" }}
        />
        <div
          className="absolute top-3/4 right-1/5 w-4 h-4 bg-gradient-to-r from-violet-500/18 to-purple-500/18 rounded-full animate-bounce"
          style={{ animationDuration: "2.4s", animationDelay: "2.2s" }}
        />
      </div>

      {/* Main authentication container */}
      <div className="relative z-10 w-full max-w-md">
        {/* Header section */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            Welcome Back
          </h1>
          <p className="text-muted-foreground">
            Sign in to your Svaasthy account or create a new one
          </p>
        </div>

        {/* Authentication card */}
        <div className="relative">
          <div className="p-8 rounded-3xl bg-card/80 backdrop-blur-sm border border-border shadow-xl">
            <Tabs defaultValue="signin" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger
                  value="signin"
                  className="data-[state=active]:bg-background data-[state=active]:text-foreground"
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Sign In
                </TabsTrigger>
                <TabsTrigger
                  value="signup"
                  className="data-[state=active]:bg-background data-[state=active]:text-foreground"
                >
                  <User className="w-4 h-4 mr-2" />
                  Sign Up
                </TabsTrigger>
              </TabsList>

              {/* Sign In Tab */}
              <TabsContent value="signin" className="space-y-6">
                <form onSubmit={handleSignIn} className="space-y-5">
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      type="tel"
                      name="phone"
                      placeholder="Phone Number"
                      required
                      value={signInPhone}
                      onChange={handleSignInChange}
                      className="pl-10 h-12 rounded-xl"
                    />
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full h-12 rounded-xl"
                    onClick={() => navigate("/face-id")}
                  >
                    <ScanFace className="w-4 h-4 mr-2" />
                    Login with Face ID
                  </Button>
                </form>
              </TabsContent>

              {/* Sign Up Tab */}
              <TabsContent value="signup" className="space-y-6">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      type="text"
                      name="firstName"
                      placeholder="First Name"
                      required
                      value={signupData.firstName}
                      onChange={handleChange}
                      className="h-12 rounded-xl"
                    />
                    <Input
                      type="text"
                      name="lastName"
                      placeholder="Last Name"
                      required
                      value={signupData.lastName}
                      onChange={handleChange}
                      className="h-12 rounded-xl"
                    />
                  </div>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      type="tel"
                      name="phone"
                      placeholder="Phone Number"
                      required
                      value={signupData.phone}
                      onChange={handleChange}
                      className="pl-10 h-12 rounded-xl"
                    />
                  </div>

                  {/* Date of Birth Picker */}
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
                        }}
                      />
                    </PopoverContent>
                  </Popover>

                  {/* Gender Select */}
                  <Select
                    onValueChange={handleGenderChange}
                    value={signupData.gender}
                  >
                    <SelectTrigger className="w-full h-12 rounded-xl">
                      <SelectValue placeholder="Select Gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                      <SelectItem value="prefer_not_say">
                        Prefer not to say
                      </SelectItem>
                    </SelectContent>
                  </Select>

                  <Button
                    type="submit"
                    className="w-full h-12 rounded-xl"
                    disabled={loading}
                    onClick={() => navigate('/otp')}
                  >
                    <User className="w-4 h-4 mr-2" />
                    {loading ? "Creating Account..." : "Create Account"}
                  </Button>

                  {msg && (
                    <div className="p-3 rounded-xl bg-destructive/10 border border-destructive/20">
                      <p className="text-center text-destructive text-sm">
                        {msg}
                      </p>
                    </div>
                  )}
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
