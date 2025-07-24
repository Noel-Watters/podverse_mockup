import { Feed } from './feed';
import {Item} from './item';
import {Stats} from './stats';
export interface Channel {
    id: number;
    id_text: string;
    slug: string;
    feed_id: number;
    podcast_index_id?: number;
    podcast_guid: string;
    title: string;
    sortable_title: string;
    medium_id: number;
    has_podcast_idex_value: boolean;
    has_value_time_splits: boolean
    category: Category[];
    medium: Medium;
}

export interface Category {
    id: number;
    display_name: string;
    mapping_key: string;
    parent_id?: number;
    slug: string;
}

export interface Medium {
    id: number;
    value: string;
}

export interface ChannelData {
  id: number;
  title: string;
  podcast_index_id: number;
  id_text: string;
  slug: string;
  medium_id: number;
  categories: Category[];
  medium: Medium;
  feed: Feed;
  items: Item[];
  stats: Stats[];
}