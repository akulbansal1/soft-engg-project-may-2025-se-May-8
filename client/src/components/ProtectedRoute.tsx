import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./ui/Spinner"; // Import the new Spinner component

const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    // Display the spinner in the center of the screen
    return (
      <div className="flex h-[calc(100dvh-200px)] w-full items-center justify-center">
        <Spinner className="h-8 w-8 text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
