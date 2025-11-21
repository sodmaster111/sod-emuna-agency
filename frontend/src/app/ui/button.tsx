import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

const baseClasses =
  "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-primary)] disabled:cursor-not-allowed disabled:opacity-70";

const variantClasses = {
  primary:
    "bg-[var(--color-primary)] text-black shadow-lg shadow-[var(--color-primary)]/20 hover:-translate-y-0.5 hover:shadow-xl",
  secondary:
    "border border-[var(--color-border)] text-[var(--color-text)] hover:-translate-y-0.5 hover:border-[var(--color-accent)]",
  ghost: "text-[var(--color-text)] hover:bg-white/5",
} as const;

const sizeClasses = {
  sm: "px-3 py-2 text-sm",
  md: "px-4 py-2.5 text-sm",
  lg: "px-5 py-3 text-base",
} as const;

function cn(...inputs: Array<string | undefined | false | null>) {
  return twMerge(clsx(inputs));
}

export type ButtonVariant = keyof typeof variantClasses;
export type ButtonSize = keyof typeof sizeClasses;

export type ButtonProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  asChild?: boolean;
  href?: string;
  className?: string;
  children: React.ReactNode;
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "color"> &
  Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, "color">;

export const Button = React.forwardRef<HTMLElement, ButtonProps>(function Button(
  {
    variant = "primary",
    size = "md",
    asChild = false,
    href,
    className,
    children,
    ...rest
  },
  forwardedRef,
) {
  const { type, ...restProps } = rest as {
    type?: React.ButtonHTMLAttributes<HTMLButtonElement>["type"];
  } & Record<string, unknown>;

  const shouldRenderSlot = asChild && React.isValidElement(children);
  const Component: React.ElementType = shouldRenderSlot ? Slot : href ? "a" : "button";

  const mergedClassName = cn(baseClasses, variantClasses[variant], sizeClasses[size], className);

  const componentProps = {
    ...restProps,
    className: mergedClassName,
    ...(Component === "a" ? { href } : { type: type ?? "button" }),
  };

  return (
    <Component ref={forwardedRef as React.Ref<HTMLElement>} {...componentProps}>
      {children}
    </Component>
  );
});
