import { LandingHeader } from '../components/landing/LandingHeader';
import { HeroSection } from '../components/landing/HeroSection';
import { FeaturesSection } from '../components/landing/FeaturesSection';
import { WorkflowSection } from '../components/landing/WorkflowSection';
import { FinalCtaSection } from '../components/landing/FinalCtaSection';
import { LandingFooter } from '../components/landing/LandingFooter';
import { useScrollReveal } from '../hooks/useScrollReveal';
import './LandingPage.css';

export function LandingPage() {
  useScrollReveal();

  return (
    <div className="landing-shell">
      <LandingHeader />
      <main className="landing-main">
        <HeroSection />
        <FeaturesSection />
        <WorkflowSection />
        <FinalCtaSection />
      </main>
      <LandingFooter />
    </div>
  );
}
