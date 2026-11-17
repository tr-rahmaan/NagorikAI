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
            "name": "জাতীয় পরিচয়পত্র (NID) সংশোধন ও রি-ইস্যু",
            "official_cost_num": 230,
            "official_cost": "২৩০ টাকা (১ম বার নাম/জন্মতারিখ পরিবর্তন) | রি-ইস্যু: ২৩০ - ৩৪৫ টাকা",
            "hotline": "১০৫ (NID হেল্পডেস্ক) | ১০৬ (দুদক)",
            "warning": "NID সংশোধনের ফি শুধুমাত্র বিকাশ, রকেট, নগদ বা সরকারি ট্রেজারিতে সরাসরি জমা দিতে হয়। কোনো ব্যক্তি বা কর্মচারীকে নগদ টাকা দেওয়া সম্পূর্ণ নিষিদ্ধ।"
        },
        "passport": {
            "name": "ই-পাসপোর্ট আবেদন",
            "official_cost_num": 4025,
            "official_cost": "৪৮ পৃষ্ঠা ৫ বছর: ৪,০২৫ টাকা | ১০ বছর: ৫,৭৫০ টাকা (১৫% ভ্যাটসহ)",
            "hotline": "১৬৪৪৫ (পাসপোর্ট হেল্পলাইন) | ১০৬ (দুদক) | ৯৯৯ (পুলিশ)",
            "warning": "ই-পাসপোর্টের জন্য কোনো ফরম সত্যায়ন লাগে না এবং ছবি সাথে নিতে হয় না। দালালদের অতিরিক্ত টাকা দেওয়া আইনত দণ্ডনীয়।"
        },
        "land_mutation": {
            "name": "ই-নামজারি (Land Mutation)",
            "official_cost_num": 1170,
            "official_cost": "মোট সরকারি ফি মাত্র ১,১৭০ টাকা (আবেদনে ৭০ টাকা + মঞ্জুর হলে ১,১০০ টাকা)",
            "hotline": "১৬১২২ (ভূমি সেবা হেল্পলাইন) | ১০৬ (দুদক)",
            "warning": "ই-নামজারিতে ১,১৭০ টাকার বেশি কোনো ফি নেই। কোনো দালাল বা মধ্যস্বত্বভোগীকে অতিরিক্ত টাকা দেওয়া বেআইনি।"
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

        # Also handle Bengali numbers like আট হাজার, পাঁচ হাজার, etc.
        bn_amounts = {
            "আট হাজার": 8000, "৮০০০": 8000, "৮,০০০": 8000,
            "পাঁচ হাজার": 5000, "৫০০০": 5000, "৫,০০০": 5000,
            "দশ হাজার": 10000, "১০০০০": 10000, "১০,০০০": 10000,
            "বিশ হাজার": 20000, "২০০০০": 20000, "২০,০০০": 20000,
            "পনের হাজার": 15000, "১৫০০০": 15000, "১৫,০০০": 15000,
            "পঁচিশ হাজার": 25000, "২৫০০০": 25000, "২৫,০০০": 25000,
        }
        for phr, val in bn_amounts.items():
            if phr in query_lower and val not in high_amounts:
                high_amounts.append(val)

        is_suspicious = bool(matched_keywords or high_amounts)

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
        official_cost_num = (service_info or {}).get("official_cost_num", 0)

        # Calculate estimated savings
        difference_amount = 0
        if high_amounts and official_cost_num:
            claimed_amount = max(high_amounts)
            difference_amount = max(0, claimed_amount - official_cost_num)
        elif high_amounts:
            difference_amount = max(high_amounts)

        return {
            "flagged": True,
            "matched_keywords": matched_keywords,
            "high_amounts_detected": high_amounts,
            "difference_amount": difference_amount,
            "service": target_service,
            "service_info": service_info,
            "alert_banner_bn": "সরকারি সতর্কতা: অননুমোদিত ফি ও মধ্যস্বত্বভোগী প্রতিরোধ",
            "advice_bn": (
                "নাগরিকদের অবগতির জন্য জানানো যাচ্ছে যে, সরকারি সেবায় দালাল বা মধ্যস্বত্বভোগীকে কোনো অর্থ প্রদান সম্পূর্ণ বেআইনি এবং দণ্ডনীয় অপরাধ। "
                "সকল প্রকার ফি কেবলমাত্র সরকার নির্ধারিত চ্যানেল ও চালানের মাধ্যমে পরিশোধ করতে হবে।"
            ),
            "emergency_hotline": service_info["hotline"] if service_info else "১০৬ (দুদক) | ৩৩৩ (জাতীয় তথ্য ও সেবা)"
        }
