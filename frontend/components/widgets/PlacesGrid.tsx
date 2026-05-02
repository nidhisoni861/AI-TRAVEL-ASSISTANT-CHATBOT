import { Star, MapPin } from "lucide-react";
import type { Place } from "@/lib/types";

interface Props {
  places: Place[];
  location?: string;
  category?: string;
}

export function PlacesGrid({ places, location, category }: Props) {
  if (!places?.length) return null;
  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-4 my-2 animate-fade-in">
      <div className="flex items-center gap-2 text-sm mb-3">
        <MapPin size={16} className="text-brand-500" />
        <span className="font-medium text-slate-700 capitalize">
          {category || "Places"} {location && `in ${location}`}
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {places.slice(0, 6).map((p, i) => (
          <div key={i} className="rounded-xl border border-slate-100 p-3 hover:bg-slate-50">
            <div className="flex items-start justify-between gap-2">
              <div className="font-medium text-slate-800 leading-tight">{p.name}</div>
              {p.rating && (
                <span className="inline-flex items-center gap-0.5 text-xs text-amber-700 shrink-0">
                  <Star size={12} fill="currentColor" /> {p.rating.toFixed(1)}
                </span>
              )}
            </div>
            {p.description && (
              <div className="text-xs text-slate-500 mt-1 line-clamp-2">{p.description}</div>
            )}
            {p.address && (
              <div className="text-[11px] text-slate-400 mt-1 truncate">{p.address}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
