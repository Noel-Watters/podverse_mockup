import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import {Stats } from '@/types/stats'; 



interface FeedStatsChartsProps {
  stats: Stats;
}

const FeedStatsCharts: React.FC<FeedStatsChartsProps> = ({ stats }) => {
  const dailyData = [
    { day: '8d ago', count: stats.day_8_count },
    { day: '7d ago', count: stats.day_7_count },
    { day: '6d ago', count: stats.day_6_count },
    { day: '5d ago', count: stats.day_5_count },
    { day: '4d ago', count: stats.day_4_count },
    { day: '3d ago', count: stats.day_3_count },
    { day: 'Yesterday', count: stats.day_2_count },
    { day: 'Today', count: stats.day_1_count },
  ];

  const weeklyData = [
    { week: '4w ago', count: stats.week_4_count },
    { week: '3w ago', count: stats.week_3_count },
    { week: '2w ago', count: stats.week_2_count },
    { week: '1w ago', count: stats.week_1_count },
    { week: 'Current', count: stats.week_current_count },
  ];

  const monthlyData = [
    { month: 'Last Month', count: stats.month_1_count },
    { month: 'This Month', count: stats.month_current_count },
  ];

  return (
    <div className="space-y-12 py-6">
      {/* Daily Line Chart */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Daily Downloads (Last 8 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Weekly Bar Chart */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Weekly Downloads</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={weeklyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Bar Chart */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Monthly Comparison</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#ffc658" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default FeedStatsCharts;
