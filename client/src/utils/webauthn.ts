export async function registerCredential(username: string): Promise<Credential | null> {
  const publicKey: PublicKeyCredentialCreationOptions = {
    challenge: crypto.getRandomValues(new Uint8Array(32)),
    rp: { name: "Local App" },
    user: {
      id: Uint8Array.from(username, c => c.charCodeAt(0)),
      name: username,
      displayName: username,
    },
    pubKeyCredParams: [{ type: "public-key", alg: -7 }],
    authenticatorSelection: {
      authenticatorAttachment: "platform",
      userVerification: "required",
    },
    timeout: 60000,
    attestation: "none",
  };

  const credential = await navigator.credentials.create({
    publicKey,
  }) as PublicKeyCredential | null;
  return credential;
}

export async function authenticateCredential(credentialId: string): Promise<Credential | null> {
  const publicKey: PublicKeyCredentialRequestOptions = {
    challenge: crypto.getRandomValues(new Uint8Array(32)),
    allowCredentials: [
      {
        type: "public-key",
        id: Uint8Array.from(atob(credentialId), c => c.charCodeAt(0)),
        transports: ["internal"],
      },
    ],
    userVerification: "required",
    timeout: 60000,
  };

  const assertion = await navigator.credentials.get({
    publicKey,
  }) as PublicKeyCredential | null;
  
  return assertion;
}