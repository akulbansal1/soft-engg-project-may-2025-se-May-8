import { Fingerprint, Heart, Lock, Shield } from "lucide-react";
import React from "react";

const BackgroundAnimation: React.FC = () => {
  return (
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
  );
};

export default BackgroundAnimation;
