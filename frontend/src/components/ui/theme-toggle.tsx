import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/context/ThemeContext";
import { cn } from "@/lib/utils";

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className={cn(
        "relative rounded-full h-9 w-9",
        "hover:bg-primary/10 transition-all duration-300"
      )}
      title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
    >
      <Sun
        className={cn(
          "h-5 w-5 rotate-0 scale-100 transition-all duration-300",
          theme === "dark" && "rotate-90 scale-0"
        )}
      />
      <Moon
        className={cn(
          "absolute h-5 w-5 rotate-90 scale-0 transition-all duration-300",
          theme === "dark" && "rotate-0 scale-100"
        )}
      />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
};
