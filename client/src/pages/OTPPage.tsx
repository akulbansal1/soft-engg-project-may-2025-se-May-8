import React from "react";
import { useNavigate } from "react-router-dom";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";
import { Button } from "@/components/ui/button";

const OTPPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSubmit = () => {
    // validate OTP logic here
    navigate("/home");
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col justify-between p-4">
      {/* Header and Instructions */}
      <div className="max-w-sm w-full mx-auto">
        <h2 className="text-2xl font-semibold text-center mb-2">
          Enter Verification Code
        </h2>
        <p className="text-center text-muted-foreground">
          We sent a 6-digit code to your phone number. Please enter it below.
        </p>
        <div className="flex-grow flex items-center justify-center mt-10">
          <InputOTP maxLength={6}>
            <InputOTPGroup>
              <InputOTPSlot index={0} />
              <InputOTPSlot index={1} />
              <InputOTPSlot index={2} />
            </InputOTPGroup>
            <InputOTPSeparator />
            <InputOTPGroup>
              <InputOTPSlot index={3} />
              <InputOTPSlot index={4} />
              <InputOTPSlot index={5} />
            </InputOTPGroup>
          </InputOTP>
        </div>
      </div>

      {/* Bottom Sign In Button */}
      <div className="w-full max-w-sm mx-auto">
        <Button onClick={handleSubmit} className="w-full mt-4">
          Sign In
        </Button>
      </div>
    </div>
  );
};

export default OTPPage;
