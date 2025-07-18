"use client";
import React from 'react';

export default function DashboardHeader() {
  return (
    <section className="text-center space-y-2">
      <h1 className="text-2xl font-bold">Welcome to the Podverse Admin Dashboard</h1>
      <p className="text-gray-600">Manage your application effortlessly.</p>
      <div className="flex justify-center gap-4">
        <button className="px-4 py-2 border border-border  rounded">Manage RSS Feeds</button>
        <button className="px-4 py-2 bg-primary border border-border text-white rounded">Detailed Metrics</button>
      </div>
    </section>
  );
}
