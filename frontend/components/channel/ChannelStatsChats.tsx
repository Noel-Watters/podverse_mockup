import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import {Stats } from '@/types/stats'; 
import { FunnelIcon } from '@heroicons/react/24/outline';



interface ChannelStatsChartsProps {
  stats: Stats;
}

const ChannelStatsCharts: React.FC<ChannelStatsChartsProps> = ({ stats }) => {
  const [selectedView, setSelectedView] = useState<'daily' | 'weekly' | 'monthly'>('daily');
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
      <div className="flex items-center justify-between mb-2">
  <h2 className="text-xl font-semibold">
    {selectedView === 'daily' && 'Daily Views (Last 8 Days)'}
    {selectedView === 'weekly' && 'Weekly Views'}
    {selectedView === 'monthly' && 'Monthly Comparison'}
  </h2>
  <div className="relative w-32 min-w-[90px] h-8 text-left border border-black rounded-md px-2 py-1 text-sm text-black bg-white focus:outline-none flex items-center">
    <select
      onChange={e => setSelectedView(e.target.value as 'daily' | 'weekly' | 'monthly')}
      className="appearance-none border-none w-full h-full pr-6 bg-transparent focus:outline-none focus:ring-0"
      value={selectedView}
    >
      <option value="daily">Daily</option>
      <option value="weekly">Weekly</option>
      <option value="monthly">Monthly</option>
    </select>
    <FunnelIcon className="h-4 w-4 text-black absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
  </div>
</div>
      {/* Daily Line Chart */}
      {selectedView === 'daily' && (
      <div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar  dataKey="count" fill="#0d79b3e0" radius={[8, 8, 0, 0]}  stroke='#000000e3' strokeWidth={1} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      )}


      {selectedView === 'weekly' && (
        <div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#0d7ab3" radius={[8, 8, 0, 0]}  stroke='#000000e3' strokeWidth={1} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}


      {selectedView === 'monthly' && (
        <div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#0d7ab3" radius={[8, 8, 0, 0]}  stroke='#000000e3' strokeWidth={1} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      
    </div>
  );
};

export default ChannelStatsCharts;
