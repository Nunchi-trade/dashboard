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
          totalMembers: 0,
          totalHouseCapital: 0,
          houseApy: 0,
          houseProducts: [],
          totalPlayers: 0,
          cumulativeVolume: 0,
          dayVolume: 0,
          playerMarkets: [],
        },
      },
    };
  }
};

export default function Home({ metrics }: HomeProps) {
  const [activeTab, setActiveTab] = useState<"house" | "players">("house");

  return (
    <>
      <Head>
        <title>Nunchi House Stats</title>
        <meta name="description" content="Nunchi institutional dashboard" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </Head>

      <div className="min-h-screen bg-background">
        <Navbar />

        <main className="max-w-[1217px] mx-auto px-6 md:px-12 pt-8 pb-4">
          <PageHeader />

          <div className="mt-6">
            <TabToggle active={activeTab} onChange={setActiveTab} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <HousePanel
              totalMembers={metrics.totalMembers}
              totalCapital={metrics.totalHouseCapital}
              apy={metrics.houseApy}
              products={metrics.houseProducts}
            />
            <PlayersPanel
              totalPlayers={metrics.totalPlayers}
              cumulativeVolume={metrics.cumulativeVolume}
              dayVolume={metrics.dayVolume}
              markets={metrics.playerMarkets}
            />
          </div>
        </main>
      </div>
    </>
  );
}
