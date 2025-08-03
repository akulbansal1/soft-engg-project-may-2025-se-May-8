import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";
import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import {decodeFirst} from "cbor-web";

const OTPPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [verified, setVerified] = useState(false);
  const [proceeding, setProceeding] = useState(false);

  const validData = (location.state as { user_info: any })?.user_info;
  const phone = validData?.phone;

  const handleOTPSubmit = async () => {
    setError("");
    if (!otp || otp.length !== 6) {
      setError("Please enter a valid 6-digit code.");
      return;
    }
    if (!phone) {
      setError("Phone number missing.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/v1/auth/sms/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: otp,
          phone: phone.startsWith("+") ? phone : `+${phone}`,
        }),
      });

      if (!response.ok) {
        const errRes = await response.json();
        throw new Error(errRes.message || "OTP verification failed.");
      }

      const result = await response.json();
      console.log("✅ OTP verified:", result);
      setVerified(true);
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
      console.error("❌ OTP error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePasskeySetup = async () => {
    setError("");
    setProceeding(true);
    setLoading(true);

    try {
      const userData = {
        user_phone: phone.startsWith("+") ? phone : `+${phone}`,
        user_name: `${validData.firstName} ${validData.lastName}`,
        user_dob: validData.dob,
        user_gender: validData.gender,
      };

      const challengeRes = await fetch("/api/v1/auth/passkey/register/challenge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });

      if (!challengeRes.ok) {
        throw new Error("Failed to get passkey challenge");
      }

      const challengeData = await challengeRes.json();

      const publicKeyOptions: PublicKeyCredentialCreationOptions = {
        challenge: Uint8Array.from(atob(challengeData.challenge), (c) => c.charCodeAt(0)),
        rp: challengeData.rp,
        user: {
          id: Uint8Array.from(atob(challengeData.user.id), (c) => c.charCodeAt(0)),
          name: challengeData.user.name,
          displayName: challengeData.user.display_name,
        },
        pubKeyCredParams: [
          { type: "public-key", alg: -7 },
          { type: "public-key", alg: -257 },
        ],
        timeout: challengeData.timeout,
        attestation: challengeData.attestation,
      };

      const credential = (await navigator.credentials.create({
        publicKey: publicKeyOptions,
      })) as PublicKeyCredential;

      const attestationResponse = credential.response as AuthenticatorAttestationResponse;
      const attestationObject = new Uint8Array(attestationResponse.attestationObject);
      const decodedAttestation = await decodeFirst(attestationObject.buffer);

      // Get public key bytes from decoded CBOR
      const publicKeyBytes = decodedAttestation.authData.slice(-65); // ES256 public key is 65 bytes
      const publicKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(publicKeyBytes)));


      const credentialData = {
        request: userData,
        response_data: {
          credential_id: credential.id,
          public_key: publicKeyBase64, // now included
          attestation_object: btoa(
            String.fromCharCode(...new Uint8Array(attestationResponse.attestationObject))
          ),
          client_data_json: btoa(
            String.fromCharCode(...new Uint8Array(attestationResponse.clientDataJSON))
          ),
        },
      };



      const verifyRes = await fetch("/api/v1/auth/passkey/register/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentialData),
      });

      if (!verifyRes.ok) {
        const errorData = await verifyRes.json();
        console.error("Passkey verification error:", errorData);
        throw new Error("Passkey verification failed");
      }

      const result = await verifyRes.json();
      console.log("✅ Passkey registered successfully:", result);

      navigate("/home");
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
      console.error("❌ Registration error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col justify-between p-4">
      <div className="max-w-sm w-full mx-auto">
        <h2 className="text-2xl font-semibold text-center mb-2">
          Enter Verification Code
        </h2>
        <p className="text-center text-muted-foreground">
          We sent a 6-digit code to your phone number. Please enter it below.
        </p>

        <div className="flex-grow flex items-center justify-center mt-10 min-h-[80px]">
          {verified ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className="text-green-500"
            >
              <CheckCircle2 size={64} />
            </motion.div>
          ) : (
            <InputOTP value={otp} onChange={setOtp} maxLength={6}>
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
          )}
        </div>

        {error && (
          <p className="text-sm text-red-500 text-center mt-4">{error}</p>
        )}
      </div>

      <div className="w-full max-w-sm mx-auto">
        <Button
          onClick={verified ? handlePasskeySetup : handleOTPSubmit}
          className="w-full mt-4"
          disabled={loading}
        >
          {loading
            ? verified
              ? "Setting up..."
              : "Verifying..."
            : verified
            ? "Proceed to setup passkey/biometric"
            : "Verify OTP"}
        </Button>
      </div>
    </div>
  );
};

export default OTPPage;