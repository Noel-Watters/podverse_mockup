"use client";
//Used to display a pie chart on Dashboard
import React from "react";
import { PieChart, Pie, Cell, Legend, ResponsiveContainer } from "recharts";

interface FeedStatsChartProps {
  healthy: number;
  flagged: number;
}

const COLORS = ["#0d7ab3", "#b1cae3"];

export default function FeedStatsChart({ healthy, flagged }: FeedStatsChartProps) {
  const data = [
    { name: "Healthy", value: healthy },
    { name: "Flagged", value: flagged },
  ];
  const COLORS = [
    "#0d7ab3", // Healthy
    "#e53e3e"  // Flagged (red for more contrast)
  ];
  const RADIAN = Math.PI / 180;
  // Custom label rendering for modern look
  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
    index,
  }: {
    cx: number;
    cy: number;
    midAngle: number;
    innerRadius: number;
    outerRadius: number;
    percent: number;
    index: number;
  }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 1.2;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    return (
      <text
        x={x}
        y={y}
        fill="#222"
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontWeight="bold"
        fontSize={18}
        style={{ textShadow: "0 1px 4px #fff" }}
      >
        {`${data[index].name}: ${(percent * 100).toFixed(1)}%`}
      </text>
    );
  };

  return (
    <div className="w-full h-[400px] flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-100 rounded-xl shadow-lg p-6 relative">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={90}
            outerRadius={140}
            labelLine={false}
            label={renderCustomizedLabel}
            stroke="#fff"
            strokeWidth={3}
            isAnimationActive={true}
          >
            {data.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            wrapperStyle={{ fontSize: "1.1rem", fontWeight: "bold", color: "#222" }}
          />
        </PieChart>
      </ResponsiveContainer>
      {/* Modern overlay effect */}
      <div className="absolute inset-0 pointer-events-none rounded-xl border-2 border-blue-200 opacity-30"></div>
    </div>
  );
}
