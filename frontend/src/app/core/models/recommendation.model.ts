export interface ClusterReco {
  cluster_id: number;
  client_type: string;
  description: string;
  product_category: string;
  offer_type: string;
  channels: string[];
  budget: number;
  currency: string;
  roi_estimate: number;
  target_size: number;
  target_pct: number;
}

export interface Recommendation {
  id: string;
  season: string;
  currency: string;
  total_budget: number | null;
  clusters: { items: ClusterReco[] };
  model_version: string | null;
  created_at: string;
  dataset_name?: string;
}

export interface GenerateRequest {
  dataset_id: string;
  season: string;
  currency: string;
  total_budget: number;
  channels: string[];
}
