export interface FeedLog {
  id: number;
  feed_id: number;
  http_status?: number;
  is_success?: boolean;
  parse_errors?: number;
  parse_error_message?: string;
  started_at?: string;
  finished_at?: string;
  parsed_by?: string;
  last_finished_parse_time?: string;
}

export interface Feed {
  id: number;
  flag_status: string;
  url: string;
  last_parsed_file_hash?: string;
  parsing_priority?: number;
  container_id?: string;
  created_at?: string;
  updated_at?: string;
  is_parsing?: boolean;
  logs?: FeedLog[];
  recent_logs?: FeedLog[];
}

export interface FeedFlagStatus {
  id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface FeedFilters {
  status: string;
  parsing_priority?: number;
  is_parsing?: boolean;
  sort_by?: string;
  sort_order?: string;
  searchTerm?: string;
  limit?: number;
  page?: number;
}

export interface FeedStatusInfo {
  id: number;
  label: string;
  className: string;
}

export const FEED_STATUS_MAP: Record<string, FeedStatusInfo> = {
  active:           { id: 1, label: "Active", className: "bg-green-500 text-white" },
  "always-parse":   { id: 2, label: "Always Parse", className: "bg-green-500 text-white" },
  spam:             { id: 3, label: "Spam", className: "bg-yellow-400 text-white" },
  "pending-archive":{ id: 4, label: "Pending Archive", className: "bg-yellow-400 text-blue-900" },
  archived:         { id: 5, label: "Archived", className: "bg-gray-500 text-white" },
  takedown:         { id: 6, label: "Takedown", className: "bg-yellow-400 text-white" },
  parse_error:      { id: 7, label: "Parse Error", className: "bg-red-400 text-black" },
  fetch_error:      { id: 8, label: "Fetch Error", className: "bg-red-400 text-white" },
  "":               { id: 0, label: "Unknown", className: "bg-gray-300 text-black" }
};