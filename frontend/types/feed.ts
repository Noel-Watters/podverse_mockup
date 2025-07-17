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
  sort?: 'created_at' | 'updated_at' | 'parsing_priority' | 'status' | 'id';
  order?: 'asc' | 'desc';
  search?: string;
}