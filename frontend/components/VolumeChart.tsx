import React, { useMemo } from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface VolumeChartProps {
  title: string;
  dates: string[];
  values: number[];
}

function formatTick(v: number): string {
  if (v === 0) return "$0";
  if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(1)}M`;
  if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${v.toFixed(0)}`;
}

function niceTickValues(maxVal: number): number[] {
  if (maxVal <= 0) return [0];
  // Pick a nice step size
  const candidates = [
    1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5,
    1e6, 2e6, 5e6, 1e7, 2e7, 5e7, 1e8, 2e8, 5e8,
    1e9, 2e9, 5e9,
  ];
  let step = candidates[0];
  for (const c of candidates) {
    if (maxVal / c <= 6) { step = c; break; }
  }
  const ticks: number[] = [0];
  let v = step;
  while (v <= maxVal * 1.1) {
    ticks.push(v);
    v += step;
  }
  return ticks;
}

export default function VolumeChart({ title, dates, values }: VolumeChartProps) {
  const maxVal = useMemo(() => Math.max(...values, 0), [values]);
  const tickVals = useMemo(() => niceTickValues(maxVal), [maxVal]);
  const tickText = useMemo(() => tickVals.map(formatTick), [tickVals]);

  return (
    <div className="bg-white border border-border rounded-[7px] p-[25px] flex flex-col gap-4">
      <h3 className="text-sm italic text-dark leading-5">{title}</h3>
      <div className="w-full" style={{ height: 420 }}>
        <Plot
          data={[
            {
              x: dates,
              y: values,
              type: "scatter",
              mode: "lines",
              fill: "tozeroy",
              fillcolor: "rgba(0,201,80,0.08)",
              line: { color: "#00C950", width: 2, shape: "spline" },
              hovertemplate: "%{x}<br>$%{y:,.0f}<extra></extra>",
            },
          ]}
          layout={{
            autosize: true,
            margin: { l: 60, r: 10, t: 10, b: 50 },
            xaxis: {
              showgrid: true,
              gridcolor: "rgba(216,210,216,0.4)",
              tickfont: { size: 10, color: "#4A4450" },
              tickangle: 0,
            },
            yaxis: {
              showgrid: true,
              gridcolor: "rgba(216,210,216,0.4)",
              tickfont: { size: 10, color: "#4A4450" },
              tickvals: tickVals,
              ticktext: tickText,
            },
            plot_bgcolor: "white",
            paper_bgcolor: "white",
            showlegend: false,
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler
        />
      </div>
    </div>
  );
}
