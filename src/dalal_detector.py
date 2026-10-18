"""
Dalal-Free Protection Engine: Detects middlemen traps, suspicious unofficial fees,
and alerts citizens with official fee comparisons and reporting hotlines.
"""

import re
from typing import Dict, Any, Optional

class DalalDetector:
    # Common Bangla & English keywords associated with middlemen, bribes, extra fees
    DALAL_KEYWORDS = [
        "দালাল", "ঘুষ", "টাকা চাচ্ছে", "টাকা চায়", "অতিরিক্ত টাকা", "অতিরিক্ত ফি",
        "হাতে হাতে", "কমিশন", "স্পিড মানি", "খরচ কত লাগবে", "কনট্রাক্ট", "কন্ট্রাক্ট",
        "দালাল ছাড়া", "দালাল ধরে", "তহশিলদার টাকা", "পুলিশ টাকা", "আট হাজার", "দশ হাজার",
        "পনের হাজার", "বিশ হাজার", "পঞ্চাশ হাজার", "bribe", "middleman", "extra money",
        "agent", "illegal fee", "unofficial fee", "দালালের খপ্পর", "হয়রানি", "অফিসার টাকা চায়"
    ]

    OFFICIAL_FEES_SUMMARY = {
        "nid": {
            "name": "জাতীয় পরিচয়পত্র (NID) সংশোধন",
            "official_cost": "২৩০ টাকা (১ম বার নাম/জন্মতারিখ পরিবর্তন) | রি-ইস্যু: ২৩০ - ৩৪৫ টাকা",
            "hotline": "১০৫ (NID উইং হেল্পডেস্ক) বা ১০৬ (দুদক)",
            "warning": "NID সংশোধনের ফি শুধুমাত্র বিকাশ/রকেট/নগদে সরকারি ট্রেজারিতে সরাসরি জমা দিতে হয়। কোনো অফিসার বা ব্যক্তিকে নগদ টাকা দেওয়া সম্পূর্ণ নিষিদ্ধ।"
        },
        "passport": {
            "name": "ই-পাসপোর্ট আবেদন",
            "official_cost": "৪৮ পৃষ্ঠা ৫ বছর: ৪,০২৫ টাকা | ১০ বছর: ৫,৭৫০ টাকা (১৫% ভ্যাটসহ)",
            "hotline": "১৬৪৪৫ (পাসপোর্ট হেল্পলাইন) বা ১০৬ (দুদক) বা ৯৯৯ (পুলিশ)",
            "warning": "ই-পাসপোর্টের জন্য কোনো ফরম সত্যায়ন লাগে না, ছবি সাথে নিতে হয় না। দালালরা যে ৫,০০০-২০,০০০ টাকা দাবি করে তা সম্পূর্ণ অবৈধ।"
        },
        "land_mutation": {
            "name": "ই-নামজারি (Land Mutation)",
            "official_cost": "মোট সরকারি ফি মাত্র ১,১৭০ টাকা (আবেদনে ৭০ টাকা + মঞ্জুর হলে ১,১০০ টাকা)",
            "hotline": "১৬১২২ (ভূমি সেবা ২৪/৭) বা ১০৬ (দুদক)",
            "warning": "ই-নামজারিতে ১,১৭০ টাকার এক পয়সাও বেশি দেওয়া আইনত অপরাধ। কোনো দালাল বা তহশিলদারকে অতিরিক্ত টাকা দেবেন না।"
        }
    }

    @classmethod
    def scan_query(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Scans a user query for mentions of bribes, middlemen, or suspicious fees.
        Returns warning payload if detected.
        """
        query_lower = query.lower()
        matched_keywords = [kw for kw in cls.DALAL_KEYWORDS if kw in query_lower]
        
        # Check for numeric amounts in query like "5000 টাকা", "10000", etc.
        money_matches = re.findall(r'(\d+[\d,]*)\s*(টাকা|tk|bdt)?', query_lower)
        high_amounts = []
        for amount_str, _ in money_matches:
            clean_str = amount_str.replace(",", "")
            if clean_str.isdigit():
                val = int(clean_str)
                if val >= 2000:
                    high_amounts.append(val)

        is_suspicious = bool(matched_keywords or (high_amounts and any(k in query_lower for k in ["ফি", "খরচ", "লাগবে", "দেওয়া", "চাচ্ছে"])))

        if not is_suspicious:
            return None

        # Determine which service is relevant
        target_service = "general"
        if any(term in query_lower for term in ["পাসপোর্ট", "passport"]):
            target_service = "passport"
        elif any(term in query_lower for term in ["এনআইডি", "nid", "ভোটার", "পরিচয়পত্র"]):
            target_service = "nid"
        elif any(term in query_lower for term in ["নামজারি", "খারিজ", "জমি", "খতিয়ান", "mutation"]):
            target_service = "land_mutation"

        service_info = cls.OFFICIAL_FEES_SUMMARY.get(target_service)

        return {
            "flagged": True,
            "matched_keywords": matched_keywords,
            "high_amounts_detected": high_amounts,
            "service": target_service,
            "service_info": service_info,
            "alert_banner_bn": "🚨 দালাল ও অতিরিক্ত ফি সতর্কতা (Dalal-Free Alert)",
            "advice_bn": (
                f"সতর্কতা: আপনার প্রশ্নে অতিরিক্ত ফি বা মধ্যস্বত্বভোগীর ইঙ্গিত পাওয়া গেছে। "
                f"সরকারি সেবায় দালালকে অর্থ প্রদান বা অতিরিক্ত ফি দাবি সম্পূর্ণ বেআইনি ও দণ্ডনীয় অপরাধ।"
            ),
            "emergency_hotline": service_info["hotline"] if service_info else "১০৬ (দুদক) বা ৩৩৩ (জাতীয় তথ্য ও সেবা)"
        }
