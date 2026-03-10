import React from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface VolumeChartProps {
  title: string;
  dates: string[];
  values: number[];
}

export default function VolumeChart({ title, dates, values }: VolumeChartProps) {
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
              tickprefix: "$",
              tickformat: ".2s",
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
