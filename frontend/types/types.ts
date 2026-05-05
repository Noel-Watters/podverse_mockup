export interface Podcast {
  id: string;
  title: string;
  title_original?: string;      
  publisher: string;
  publisher_original?: string;  
  image: string;
  thumbnail?: string;           
  episodeCount?: number;
  total_episodes?: number;      
  rating?: number;
  category?: string;
}

export interface Genre {
  id: number;
  name: string;
}