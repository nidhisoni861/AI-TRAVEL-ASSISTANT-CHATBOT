import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export function newSessionId() {
  return "s-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

/**
 * Detects the BCP-47 language tag from text using Unicode script ranges and
 * common word patterns. Returns a best-effort locale string for use with
 * SpeechSynthesisUtterance.lang. Falls back to "en-US".
 */
export function detectLanguage(text: string): string {
  if (!text) return "en-US";
  // Gujarati: U+0A80–U+0AFF
  if (/[઀-૿]/.test(text)) return "gu-IN";
  // Devanagari (Hindi, Marathi, etc.): U+0900–U+097F
  if (/[ऀ-ॿ]/.test(text)) return "hi-IN";
  // Arabic: U+0600–U+06FF
  if (/[؀-ۿ]/.test(text)) return "ar-SA";
  // Chinese (CJK Unified): U+4E00–U+9FFF
  if (/[一-鿿]/.test(text)) return "zh-CN";
  // Japanese Hiragana/Katakana: U+3040–U+30FF
  if (/[぀-ヿ]/.test(text)) return "ja-JP";
  // Korean: U+AC00–U+D7AF
  if (/[가-힯]/.test(text)) return "ko-KR";
  // German: German-specific characters + common German words
  if (
    /[äöüßÄÖÜ]/.test(text) &&
    /\b(ich|Sie|und|oder|aber|nicht|auch|sind|haben|werden|für|mit|nach|von|zu|eine|einen|einer|das|die|der|ein)\b/i.test(text)
  )
    return "de-DE";
  // French: French-specific characters + common French words
  if (
    /[àâéèêëîïôùûüÿçæœÀÂÉÈÊËÎÏÔÙÛÜŸÇÆŒ]/.test(text) &&
    /\b(je|vous|nous|ils|elles|est|sont|une|les|des|dans|avec|pour|sur|pas)\b/i.test(text)
  )
    return "fr-FR";
  // Spanish: Spanish-specific characters + common Spanish words
  if (
    /[áéíóúüñÁÉÍÓÚÜÑ¿¡]/.test(text) &&
    /\b(el|la|los|las|un|una|es|son|para|con|por|del|al|que|en)\b/i.test(text)
  )
    return "es-ES";
  return "en-US";
}
