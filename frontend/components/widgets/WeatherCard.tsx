import { Cloud, Droplets, Thermometer } from "lucide-react";
import type { WeatherData } from "@/lib/types";

export function WeatherCard({ data }: { data: WeatherData }) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-sky-100 to-blue-50 border border-sky-200 p-4 my-2 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-sky-700 font-medium">Weather</div>
          <div className="text-lg font-semibold">{data.city}{data.country !== "??" && `, ${data.country}`}</div>
          <div className="text-sm text-slate-600 capitalize">{data.description}</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-sky-700">{Math.round(data.temp_c)}°</div>
          <div className="text-xs text-slate-500">feels {Math.round(data.feels_like_c)}°</div>
        </div>
      </div>
      <div className="mt-3 flex gap-4 text-xs text-slate-600">
        <span className="inline-flex items-center gap-1"><Thermometer size={14} /> {Math.round(data.temp_c)}°C</span>
        <span className="inline-flex items-center gap-1"><Droplets size={14} /> {data.humidity}%</span>
        <span className="inline-flex items-center gap-1"><Cloud size={14} /> {data.description}</span>
      </div>
    </div>
  );
}
