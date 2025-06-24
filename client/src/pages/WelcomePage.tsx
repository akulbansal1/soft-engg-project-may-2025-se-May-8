import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import VariableProximity from "@/components/VariableProximity";
import { useRef } from "react";

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  return (
    <div className="relative h-[calc(100vh-120px)] lg:h-[calc(100vh-160px)] flex flex-col justify-center items-center text-center px-6 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Floating healthcare icons/shapes */}
        <div
          className="absolute top-20 left-20 w-6 h-6 rounded-full bg-green-500/20 animate-bounce"
          style={{ animationDuration: "3s", animationDelay: "0s" }}
        />
        <div
          className="absolute top-32 right-32 w-4 h-4 rounded-full bg-blue-500/30 animate-bounce"
          style={{ animationDuration: "2.5s", animationDelay: "1s" }}
        />
        <div
          className="absolute bottom-32 left-32 w-5 h-5 rounded-full bg-purple-500/25 animate-bounce"
          style={{ animationDuration: "3.5s", animationDelay: "2s" }}
        />
        <div
          className="absolute bottom-20 right-20 w-3 h-3 rounded-full bg-pink-500/20 animate-bounce"
          style={{ animationDuration: "2.8s", animationDelay: "0.5s" }}
        />

        {/* Subtle geometric patterns */}
        <div
          className="absolute top-16 left-1/4 w-12 h-12 border border-primary/10 rounded-lg rotate-45 animate-spin"
          style={{ animationDuration: "20s" }}
        />
        <div
          className="absolute bottom-24 right-1/4 w-8 h-8 border border-blue-500/15 rounded-full animate-spin"
          style={{ animationDuration: "15s", animationDirection: "reverse" }}
        />

        {/* Medical cross shapes */}
        <div className="absolute top-1/3 left-16">
          <div className="relative w-8 h-8 opacity-10">
            <div className="absolute top-2 left-0 w-8 h-4 bg-green-500 rounded-sm" />
            <div className="absolute top-0 left-2 w-4 h-8 bg-green-500 rounded-sm" />
          </div>
        </div>
        <div className="absolute bottom-1/3 right-16">
          <div className="relative w-6 h-6 opacity-15">
            <div className="absolute top-1.5 left-0 w-6 h-3 bg-blue-500 rounded-sm" />
            <div className="absolute top-0 left-1.5 w-3 h-6 bg-blue-500 rounded-sm" />
          </div>
        </div>

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
                 linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                 linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
               `,
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      {/* Floating side elements for desktop */}
      <div className="hidden lg:block absolute left-8 top-1/2 -translate-y-1/2 space-y-8">
        <div
          className="flex flex-col items-center space-y-4 animate-pulse"
          style={{ animationDuration: "3s" }}
        >
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 flex items-center justify-center backdrop-blur-sm">
            <div className="w-8 h-8 rounded-lg bg-green-500/40" />
          </div>
          <div className="text-xs text-center text-muted-foreground/60 font-medium">
            Medicine
            <br />
            Records
          </div>
        </div>

        <div
          className="flex flex-col items-center space-y-4 animate-pulse"
          style={{ animationDuration: "3s", animationDelay: "1s" }}
        >
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30 flex items-center justify-center backdrop-blur-sm">
            <div className="w-8 h-8 rounded-full bg-blue-500/40" />
          </div>
          <div className="text-xs text-center text-muted-foreground/60 font-medium">
            Appointments
            <br />
            Details
          </div>
        </div>
      </div>

      <div className="hidden lg:block absolute right-8 top-1/2 -translate-y-1/2 space-y-8">
        <div
          className="flex flex-col items-center space-y-4 animate-pulse"
          style={{ animationDuration: "3s", animationDelay: "0.5s" }}
        >
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-violet-500/20 border border-purple-500/30 flex items-center justify-center backdrop-blur-sm">
            <div className="w-8 h-8 rounded-xl bg-purple-500/40" />
          </div>
          <div className="text-xs text-center text-muted-foreground/60 font-medium">
            Secure
            <br />
            Documents
          </div>
        </div>

        <div
          className="flex flex-col items-center space-y-4 animate-pulse"
          style={{ animationDuration: "3s", animationDelay: "1.5s" }}
        >
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500/20 to-rose-500/20 border border-pink-500/30 flex items-center justify-center backdrop-blur-sm">
            <div className="w-8 h-8 rounded-2xl bg-pink-500/40" />
          </div>
          <div className="text-xs text-center text-muted-foreground/60 font-medium">
            Emergency
            <br />
            Care
          </div>
        </div>
      </div>

      {/* Main content container */}
      <div className="relative z-10 max-w-2xl mx-auto space-y-12 lg:space-y-16">
        {/* Hero section */}
        <div className="space-y-6 lg:space-y-8">
          {/* Status badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full border border-primary/30 bg-primary/10 backdrop-blur-sm hover:bg-primary/15 transition-colors duration-300">
            <div className="w-2 h-2 bg-primary rounded-full mr-2 animate-pulse" />
            <span className="text-primary text-sm font-medium">
              Healthcare Simplified
            </span>
          </div>

          {/* Main heading */}
          <h1 className="text-5xl lg:text-6xl xl:text-7xl font-bold leading-[0.9] tracking-tight">
            Welcome to{" "}
            <span className="relative inline-block">
              {/* Animated Indigo Highlight */}
              <div className="absolute -inset-x-3 -inset-y-2 bg-indigo-200/50 dark:bg-indigo-900/50 -z-10 transform -rotate-10 hover:rotate-0 transition-transform duration-300 ease-in-out rounded-lg"></div>
              <span className="relative text-slate-900 dark:text-slate-50 font-bold">
                <div ref={containerRef} style={{ position: "relative" }}>
                  <VariableProximity
                    label={
                      "Svaasthy."
                    }
                    className={"variable-proximity-demo"}
                    fromFontVariationSettings="'wght' 400, 'opsz' 9"
                    toFontVariationSettings="'wght' 1000, 'opsz' 40"
                    containerRef={containerRef}
                    radius={100}
                    falloff="linear"
                  />
                </div>
              </span>
            </span>
          </h1>

          {/* Tagline */}
          <p className="text-zinc-500 text-lg lg:text-xl font-medium leading-relaxed max-w-lg mx-auto">
            Your trusted healthcare companion designed with{" "}
            <span className="text-primary font-semibold">care</span> and{" "}
            <span className="text-primary font-semibold">simplicity</span>.
          </p>
        </div>

        {/* Trust indicators row */}
        <div className="flex items-center justify-center space-x-8 lg:space-x-12">
          <div className="flex flex-col items-center space-y-2 group cursor-pointer">
            <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-2xl bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <div className="w-3 h-3 bg-green-500 rounded-full" />
            </div>
            <span className="text-xs lg:text-sm font-medium text-muted-foreground group-hover:text-green-600 transition-colors duration-300">
              Secure
            </span>
          </div>

          <div className="flex flex-col items-center space-y-2 group cursor-pointer">
            <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <div className="w-3 h-3 bg-blue-500 rounded-full" />
            </div>
            <span className="text-xs lg:text-sm font-medium text-muted-foreground group-hover:text-blue-600 transition-colors duration-300">
              Simple
            </span>
          </div>

          <div className="flex flex-col items-center space-y-2 group cursor-pointer">
            <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <div className="w-3 h-3 bg-purple-500 rounded-full" />
            </div>
            <span className="text-xs lg:text-sm font-medium text-muted-foreground group-hover:text-purple-600 transition-colors duration-300">
              Caring
            </span>
          </div>
        </div>

        {/* CTA section */}
        <div className="space-y-4">
          <Button
            size="lg"
            onClick={() => navigate("/authentication")}
            className="w-full mx-auto text-lg font-semibold py-4 rounded-2xl transform hover:scale-[1.02] active:scale-[0.98] border border-primary/20"
          >
            <span>Get Started</span>
            <div className="ml-3 text-xl">→</div>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
