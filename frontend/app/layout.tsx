import type { Metadata } from "next";
import { ColorSchemeScript, MantineProvider } from "@mantine/core";
import "./globals.css";
import '@mantine/core/styles.css';
import { CartProvider } from "../context/CartContext";

export const metadata: Metadata = {
  title: "AI Studio",
  description: "Virtual Try-On E-commerce",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ColorSchemeScript />
      </head>
      <body>
        <MantineProvider>
          <CartProvider>
            {children}
          </CartProvider>
        </MantineProvider>
      </body>
    </html>
  );
}
