import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CgDarkMode } from "react-icons/cg";
import WelcomePage from "./pages/WelcomePage";
import Authentication from "./pages/Authentication";
import OTPPage from "./pages/OTPPage";
import FaceIDPage from "./pages/FaceIDPage";
import HomePage from "./pages/HomePage";
import EmergencyContactsPage from "./pages/EmergencyContactsPage";
import AppointmentsPage from "./pages/AppointmentsPage";
import HealthPage from "./pages/HealthPage";
import MedicinesPage from "./pages/MedicinesPage";
import DataVault from "./pages/DataVault";
import Settings from "./pages/Settings";


const App: React.FC = () => {
  const [dark, setDark] = useState<boolean>(() => {
    const stored = localStorage.getItem("theme");
    if (stored) return stored === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <BrowserRouter>
      <div className="min-h-[100dvh] sm:w-[90%] md:w-[80%] max-w-[1000px] mx-auto flex flex-col">
        <header className="flex justify-between items-center p-4 border-b">
          <h1 className="text-3xl font-bold leading-0 tracking-tight">
            SVAASTHY.
          </h1>
          <button
            onClick={() => setDark((prev) => !prev)}
            aria-label="Toggle dark mode"
            className="p-2 rounded"
          >
            <CgDarkMode
              size={24}
              className="active:scale-110 hover:cursor-pointer"
            />
          </button>
        </header>

        <main className="flex-grow w-full p-4">
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/authentication" element={<Authentication />} />
            <Route path="/otp" element={<OTPPage />} />
            <Route path="/face-id" element={<FaceIDPage />} />
            <Route path="/home" element={<HomePage />} />
            <Route
              path="/emergency-contacts"
              element={<EmergencyContactsPage />}
            />
            <Route path="/appointments" element={<AppointmentsPage />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/medicines" element={<MedicinesPage />} />
            <Route path="/data-vault" element={<DataVault />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
