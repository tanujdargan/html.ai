import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import UseCases from "@/components/UseCases";
import Comparison from "@/components/Comparison";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <Navbar />
      <Hero />
      <UseCases />
      <Comparison />
      <Footer />
    </main>
  );
}
