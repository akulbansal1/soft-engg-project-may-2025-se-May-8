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
import { useAuth } from "@/context/AuthContext";

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

const Authentication: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
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
    setSignInError("");
    if (!signInPhone) {
      setSignInError("Please enter a valid phone number.");
      return;
    }

    let credentialId = localStorage.getItem("credential_id");

    if (!credentialId) {
      setSignInError(
        "Credential ID not found. Please sign up or use a registered device."
      );
      return;
    }

    try {
      const parsedId = JSON.parse(credentialId);
      if (typeof parsedId === "string") {
        credentialId = parsedId;
      }
    } catch (e) {
      // Not a JSON string, use as is.
    }

    try {
      const challengeRes = await fetch("/api/v1/auth/passkey/login/challenge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential_id: credentialId }),
      });

      if (!challengeRes.ok) {
        throw new Error(
          "Failed to get passkey challenge. User may not be registered."
        );
      }

      const challengeData = await challengeRes.json();

      function base64urlToUint8Array(base64url: string): Uint8Array {
        const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/");
        const pad = base64.length % 4;
        const padded = base64 + (pad ? "=".repeat(4 - pad) : "");
        const binaryString = atob(padded);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes;
      }

      const publicKeyOptions: PublicKeyCredentialRequestOptions = {
        challenge: Uint8Array.from(atob(challengeData.challenge), (c) =>
          c.charCodeAt(0)
        ),
        allowCredentials: [
          { id: base64urlToUint8Array(credentialId), type: "public-key" },
        ],
        timeout: challengeData.timeout || 60000,
        rpId: "localhost",
      };

      const assertion = (await navigator.credentials.get({
        publicKey: publicKeyOptions,
      })) as PublicKeyCredential;
      const authResponse = assertion.response as AuthenticatorAssertionResponse;
      const authenticatorData = new Uint8Array(authResponse.authenticatorData);
      const dataView = new DataView(authenticatorData.buffer);
      const signCount = dataView.getUint32(33, false);

      const credentialData = {
        request: { credential_id: credentialId },
        response_data: {
          credential_id: credentialId,
          signature: btoa(
            String.fromCharCode(...new Uint8Array(authResponse.signature))
          ),
          client_data_json: btoa(
            String.fromCharCode(...new Uint8Array(authResponse.clientDataJSON))
          ),
          authenticator_data: btoa(String.fromCharCode(...authenticatorData)),
          sign_count: signCount,
        },
      };

      const verifyRes = await fetch("/api/v1/auth/passkey/login/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentialData),
      });

      if (!verifyRes.ok) {
        const errorData = await verifyRes.json();
        console.error("Passkey verification error:", errorData);
        throw new Error("Passkey verification failed");
      }

      // Step 1: Verification is successful, now fetch the user data
      const meResponse = await fetch("/api/v1/auth/me");
      if (!meResponse.ok) {
        throw new Error("Login successful, but failed to fetch user data.");
      }
      const user = await meResponse.json();

      // Step 2: Update the auth context with the user data
      if (user) {
        login(user);
        // Step 3: NOW navigate to the home page
        navigate("/home");
      } else {
        throw new Error("Failed to get user data after login.");
      }
    } catch (err: any) {
      setSignInError(err.message || "Something went wrong.");
      console.error("Login error:", err);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSignupErrors({});

    try {
      await signupSchema.validate(signupData, { abortEarly: false });
      const response = await fetch("/api/v1/auth/sms/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: signupData.phone }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to send OTP.");
      }
      navigate("/otp", { state: { user_info: signupData } });
    } catch (err: any) {
      if (err.inner) {
        const errors = err.inner.reduce((acc: any, current: any) => {
          acc[current.path] = current.message;
          return acc;
        }, {});
        setSignupErrors(errors);
      } else {
        setSignupErrors({
          form: err.message || "An unexpected error occurred.",
        });
      }
      console.log("Sign up error:", err);
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
                    <Button type="submit" className="flex-1 h-12 rounded-xl">
                      <ScanFace className="w-4 h-4 mr-2" />
                      Login with Face ID
                    </Button>
                  </div>
                </form>
              </TabsContent>

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

export default Authentication;
