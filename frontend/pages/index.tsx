import { useState } from "react";
import type { GetServerSideProps } from "next";
import Head from "next/head";
import type { DashboardData, DerivedMetrics } from "@/lib/types";
import { deriveMetrics } from "@/lib/api";
import Navbar from "@/components/Navbar";
import PageHeader from "@/components/PageHeader";
import TabToggle from "@/components/TabToggle";
import HousePanel from "@/components/HousePanel";
import PlayersPanel from "@/components/PlayersPanel";
import PlayerFeedChart from "@/components/PlayerFeedChart";
import AgentFlow from "@/components/AgentFlow";
import NetPnlChart from "@/components/NetPnlChart";
import FeedComposition from "@/components/FeedComposition";
import CompetitionSection from "@/components/CompetitionSection";
import Footer from "@/components/Footer";

interface HomeProps {
  metrics: DerivedMetrics;
}

export const getServerSideProps: GetServerSideProps<HomeProps> = async () => {
  const API_URL = process.env.API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${API_URL}/api/dashboard`);
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data: DashboardData = await res.json();
    const metrics = deriveMetrics(data);
    return { props: { metrics } };
  } catch (err) {
    console.error("Failed to fetch dashboard data:", err);
    return {
      props: {
        metrics: {
          nlpTvl: 0,
          pendleTvl: 0,
          nhypeTvl: 0,
          totalTvl: 0,
          nlpUsers: 0,
          pendleUsers: 0,
          totalLpWallets: 0,
          totalVolume: 0,
          totalWallets: 0,
          totalMarkets: 0,
          yexTotal: 0,
          competitions: [],
        },
      },
    };
  }
};

export default function Home({ metrics }: HomeProps) {
  const [activeTab, setActiveTab] = useState<"house" | "players">("house");

  const compVolumes = metrics.competitions.map((c) => ({
    label: c.name.replace("COMPETITION ", "Comp "),
    volume: c.volume,
  }));

  return (
    <>
      <Head>
        <title>Nunchi House Stats</title>
        <meta name="description" content="Nunchi institutional dashboard" />
      </Head>

      <div className="min-h-screen bg-background">
        <Navbar />

        <main className="max-w-[1600px] mx-auto px-6 md:px-12 pt-8 pb-4">
          <PageHeader />

          <div className="mt-6">
            <TabToggle active={activeTab} onChange={setActiveTab} />
          </div>

          {/* House + Players Panels */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <HousePanel
              totalTvl={metrics.totalTvl}
              lpWallets={metrics.totalLpWallets}
              nlpTvl={metrics.nlpTvl}
              pendleTvl={metrics.pendleTvl}
              nhypeTvl={metrics.nhypeTvl}
            />
            <PlayersPanel
              totalVolume={metrics.totalVolume}
              totalWallets={metrics.totalWallets}
              totalMarkets={metrics.totalMarkets}
            />
          </div>

          {/* Player Feed Chart + Agent Flow */}
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6 mt-8">
            <PlayerFeedChart compVolumes={compVolumes} />
            <AgentFlow />
          </div>

          {/* Net PnL Chart + Feed Composition */}
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6 mt-8">
            <NetPnlChart compVolumes={compVolumes} />
            <FeedComposition totalMarkets={metrics.totalMarkets} />
          </div>

          {/* Competition History */}
          <div className="mt-12">
            <CompetitionSection competitions={metrics.competitions} />
          </div>

          <Footer />
        </main>
      </div>
    </>
  );
}
