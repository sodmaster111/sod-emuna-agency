import * as React from "react";

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type BadgeProps = {
  children: React.ReactNode;
  variant?: "default" | "outline";
  className?: string;
} & React.HTMLAttributes<HTMLSpanElement>;

export function Badge({ children, variant = "default", className, ...props }: BadgeProps) {
  const baseStyles = "inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold";

  const variants: Record<NonNullable<BadgeProps["variant"]>, string> = {
    default: "bg-sod-primarySoft text-sod-primary",
    outline: "border border-sod-primary text-sod-primary bg-white",
  };

  return (
    <span className={cn(baseStyles, variants[variant], className)} {...props}>
      {children}
    </span>
  );
}
