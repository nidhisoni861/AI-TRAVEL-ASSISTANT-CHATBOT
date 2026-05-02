export type Role = "user" | "assistant";

export interface UserPreferences {
  budget?: "budget" | "mid-range" | "luxury";
  interests?: string[];
  pace?: "relaxed" | "balanced" | "packed";
  travel_style?: "solo" | "couple" | "family" | "group";
  dietary?: string[];
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: any;
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  toolCalls?: ToolCall[];
  citations?: string[];
  pending?: boolean;
}

export interface FlightOffer {
  id: string;
  airline: string;
  departure: string;
  arrival: string;
  duration: string;
  stops: number;
  price_total: number;
  currency: string;
}

export interface Place {
  name: string;
  address?: string;
  rating?: number;
  description?: string;
  image_url?: string;
}

export interface WeatherData {
  city: string;
  country: string;
  temp_c: number;
  feels_like_c: number;
  humidity: number;
  description: string;
  icon: string;
}
