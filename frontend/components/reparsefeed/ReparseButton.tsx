"use client";
import React from 'react';
import { ArrowPathIcon } from '@heroicons/react/24/outline';


interface ReparseButtonProps {
  onClick: () => void;
  loading: boolean; // will now be reparsing
  disabled?: boolean;
  status?: string;
  children?: React.ReactNode;
}

const ReparseButton: React.FC<ReparseButtonProps> = ({
  onClick,
  loading,
  disabled,
  status,
  children,
}) => (
  <button
    type="button"
    onClick={onClick}
    disabled={loading || disabled}
    className={`border border-black rounded-md p-1 bg-white hover:bg-gray-100 transition flex items-center justify-center
      ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
    aria-busy={loading}
    aria-label={status === 'pending' ? 'Reparsing...' : 'Reparse'}
  >
    <ArrowPathIcon
      className={`h-5 w-5 text-black ${loading ? 'animate-spin' : ''}`}
      aria-hidden="true"
    />
  </button>
);

export default ReparseButton;