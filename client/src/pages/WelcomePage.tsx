import React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const WelcomePage: React.FC = () => {
  return (
    <div className="flex flex-col justify-between h-full min-h-[calc(100dvh-110px)] px-4 py-8 text-center">
      <div>
        <h1 className="text-4xl font-bold mb-4">Welcome to Svaasthy</h1>
        <p className="text-muted-foreground text-md md:text-xl font-medium max-w-md mx-auto">
          Your personal companion for accessible, secure, and simplified
          healthcare — designed with care for our beloved elders.
        </p>
      </div>

      <div className="space-y-4">
        <Link to="/authentication">
          <Button className="w-full hover:cursor-pointer">Get Started.</Button>
        </Link>
      </div>
    </div>
  );
};

export default WelcomePage;
