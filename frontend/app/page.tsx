import { Hero } from "@/components/landing/Hero";
import { LandingFooter } from "@/components/landing/LandingFooter";
import { LandingNav } from "@/components/landing/LandingNav";
import { Perspectives } from "@/components/landing/Perspectives";
import { Workflow } from "@/components/landing/Workflow";

export default function LandingPage() {
  return (
    <>
      <LandingNav />
      <Hero />
      <Workflow />
      <Perspectives />
      <LandingFooter />
    </>
  );
}
