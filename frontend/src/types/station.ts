export interface Station {
  id: string
  name: string
  country: string
  latitude: number
  longitude: number
  type: string
  source: string
  description?: string
  // Added fields for thesis table (optional for backward compatibility)
  code?: string
  period?: string
  data_interval?: string
  method?: string
  status?: string
  start_year?: string
  organization?: string
  history?: string
  equipment?: string
  frequency_range?: string
}
