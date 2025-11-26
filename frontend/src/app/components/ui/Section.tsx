import * as React from "react";

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function Section({ children, className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <section className={cn("py-12 sm:py-16", className)} {...props}>
      {children}
    </section>
  );
}
