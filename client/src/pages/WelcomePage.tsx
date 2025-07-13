import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import VariableProximity from "@/components/VariableProximity";
import { useRef } from "react";
import BackgroundAnimation from "@/components/BackgroundAnimation";

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  return (
    <div className="relative h-[calc(100vh-120px)] lg:h-[calc(100vh-160px)] flex flex-col justify-center items-center text-center px-6 overflow-hidden">
      {/* Main content container */}
      <BackgroundAnimation />
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
