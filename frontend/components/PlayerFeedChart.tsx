import React, { useMemo } from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface PlayerFeedChartProps {
  compVolumes: { label: string; volume: number }[];
}

const MONTHS = [
  "Jul '25", "Aug '25", "Sep '25", "Oct '25", "Nov '25",
  "Dec '25", "Jan '26", "Feb '26", "Mar '26",
];

export default function PlayerFeedChart({ compVolumes }: PlayerFeedChartProps) {
  const { x, y, annotations } = useMemo(() => {
    // Build cumulative line from comp volumes spread across months
    const cumulative: number[] = [];
    let running = 0;
    const step = Math.max(1, Math.floor(MONTHS.length / Math.max(compVolumes.length, 1)));

    for (let i = 0; i < MONTHS.length; i++) {
      const compIdx = Math.floor(i / step);
      if (compIdx < compVolumes.length) {
        running += compVolumes[compIdx].volume / step;
      }
      cumulative.push(running);
    }

    const annots = compVolumes.map((c, idx) => ({
      x: MONTHS[Math.min(idx * step, MONTHS.length - 1)],
      label: c.label,
    }));

    return { x: MONTHS, y: cumulative, annotations: annots };
  }, [compVolumes]);

  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          Player Feed
        </p>
        <span className="text-xs border border-green/30 bg-green/5 text-green rounded-full px-3 py-1 font-medium">
          Composited Feed
        </span>
      </div>

      <div className="space-y-1">
        <h2 className="text-sm font-normal text-dark italic">
          Total Cumulative Volumes
        </h2>
        <p className="text-xs text-desc leading-relaxed">
          All competition data composited into one feed, from July 2025 to now.
        </p>
      </div>

      <div className="w-full" style={{ minHeight: 300 }}>
        <Plot
          data={[
            {
              x,
              y,
              type: "scatter" as const,
              mode: "lines" as const,
              fill: "tozeroy",
              fillcolor: "rgba(0, 201, 80, 0.08)",
              line: { color: "#00C950", width: 2, shape: "spline" },
              hovertemplate: "%{x}<br>$%{y:,.0f}<extra></extra>",
            },
          ]}
          layout={{
            autosize: true,
            height: 300,
            margin: { t: 20, r: 20, b: 40, l: 60 },
            paper_bgcolor: "#FFFFFF",
            plot_bgcolor: "#FFFFFF",
            font: { family: "Inter, sans-serif", size: 11, color: "#4A4450" },
            xaxis: {
              showgrid: false,
              tickfont: { size: 10, color: "#4A4450" },
            },
            yaxis: {
              showgrid: true,
              gridcolor: "rgba(216,210,216,0.4)",
              tickprefix: "$",
              tickfont: { size: 10, color: "#4A4450" },
            },
            shapes: annotations.map((a) => ({
              type: "line" as const,
              x0: a.x,
              x1: a.x,
              y0: 0,
              y1: 1,
              yref: "paper" as const,
              line: { color: "#D8D2D8", width: 1, dash: "dot" as const },
            })),
            annotations: annotations.map((a) => ({
              x: a.x,
              y: 1,
              yref: "paper" as const,
              text: a.label,
              showarrow: false,
              font: { size: 9, color: "#4A4450" },
              yanchor: "bottom" as const,
            })),
          }}
          config={{ displayModeBar: false, responsive: true }}
          useResizeHandler
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </div>
  );
}
