import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import Sidebar from "./components/Sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata = {
  title: "Expert Persona | Digital Twin Engine",
  description: "Extract high-fidelity AI Digital Twins from expert knowledge using the Universal Persona Extraction Framework.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} h-full antialiased`}>
      <body className="min-h-screen bg-[#030712] text-slate-200 font-[family-name:var(--font-inter)] flex">
        <Sidebar />
        <main className="flex-1 ml-72 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
