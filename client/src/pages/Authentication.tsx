import React, { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

const Authentication: React.FC = () => {
  const navigate = useNavigate();
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // Sign In state
  const [signInPhone, setSignInPhone] = useState("");
  const handleSignInChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSignInPhone(e.target.value);
  };
  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    // you can add validation here
    if (signInPhone) {
      navigate("/otp");
    } else {
      setMsg("Please enter a valid phone number");
    }
  };

  // Sign Up state
  const [signupData, setSignupData] = useState({
    firstName: "",
    middleName: "",
    lastName: "",
    phone: "",
    dob: "",
    gender: "",
  });
  const [date, setDate] = useState<Date | undefined>();
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSignupData((prev) => ({ ...prev, [name]: value }));
  };
  const handleGenderChange = (value: string) => {
    setSignupData((prev) => ({ ...prev, gender: value }));
  };
  const handleSignUp = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/otp");
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex items-center justify-center">
      <div className="w-full max-w-md rounded-2xl p-5">
        <Tabs defaultValue="signin" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-2">
            <TabsTrigger value="signin">Sign In</TabsTrigger>
            <TabsTrigger value="signup">Sign Up</TabsTrigger>
          </TabsList>

          {/* Sign In Tab */}
          <TabsContent value="signin">
            <form onSubmit={handleSignIn} className="space-y-5">
              <Input
                type="tel"
                name="phone"
                placeholder="Phone Number"
                required
                value={signInPhone}
                onChange={handleSignInChange}
              />
              <Button type="submit" className="w-full">
                Get OTP
              </Button>
              <Link to="/face-id">
                <Button type="submit" className="w-full">
                  Login with Face ID
                </Button>
              </Link>
            </form>
          </TabsContent>

          {/* Sign Up Tab */}
          <TabsContent value="signup">
            <form onSubmit={handleSignUp} className="space-y-4">
              <Input
                type="text"
                name="firstName"
                placeholder="First Name"
                required
                value={signupData.firstName}
                onChange={handleChange}
              />
              <Input
                type="text"
                name="middleName"
                placeholder="Middle Name (optional)"
                value={signupData.middleName}
                onChange={handleChange}
              />

              <Input
                type="text"
                name="lastName"
                placeholder="Last Name"
                required
                value={signupData.lastName}
                onChange={handleChange}
              />

              <Input
                type="tel"
                name="phone"
                placeholder="Phone Number"
                required
                value={signupData.phone}
                onChange={handleChange}
              />

              {/* Date of Birth Picker */}
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    data-empty={!date}
                    className="data-[empty=true]:text-muted-foreground flex items-center gap-2 w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon />
                    {date ? (
                      format(date, "yyyy-MM-dd")
                    ) : (
                      <span>Select DOB</span>
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
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Gender" />
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

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing Up…" : "Sign Up"}
              </Button>
              {msg && (
                <p className="mt-2 text-center text-destructive">{msg}</p>
              )}
            </form>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Authentication;
