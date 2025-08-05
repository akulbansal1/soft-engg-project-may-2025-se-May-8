import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading session...</div>; // Or a more stylish spinner
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
