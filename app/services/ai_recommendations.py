"""
AI Recommendations Engine - Smart Part Recommendations

This module provides intelligent part recommendations based on user behavior,
vehicle compatibility, and part relationships.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations."""
    COMPLEMENTARY = "complementary"  # Parts that work together
    ALTERNATIVE = "alternative"      # Alternative brands/models
    MAINTENANCE = "maintenance"      # Maintenance-related parts
    UPGRADE = "upgrade"             # Upgrade options
    FREQUENTLY_BOUGHT = "frequently_bought"  # Popular combinations


@dataclass
class Recommendation:
    """Represents a part recommendation."""
    part_id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    category: str
    price: Optional[float]
    availability: bool
    recommendation_score: float
    recommendation_type: RecommendationType
    reason: str
    confidence: float
    raw_data: Dict[str, Any]


@dataclass
class UserProfile:
    """User profile for personalized recommendations."""
    user_id: str
    purchase_history: List[Dict[str, Any]]
    search_history: List[str]
    preferences: Dict[str, Any]
    vehicle_info: Optional[Dict[str, str]]


class AIRecommendationsEngine:
    """
    AI-powered recommendations engine for car parts.
    """

    def __init__(self):
        self.part_relationships = self._load_part_relationships()
        self.maintenance_schedules = self._load_maintenance_schedules()
        self.brand_compatibility = self._load_brand_compatibility()
        self.popular_combinations = defaultdict(list)

    def _load_part_relationships(self) -> Dict[str, List[str]]:
        """Load part relationship mappings."""
        return {
            # Brake system relationships
            "brake_pad": ["brake_disc", "brake_caliper", "brake_fluid", "brake_sensor"],
            "brake_disc": ["brake_pad", "brake_caliper", "brake_fluid"],
            "brake_caliper": ["brake_pad", "brake_disc", "brake_fluid"],
            
            # Engine system relationships
            "air_filter": ["oil_filter", "fuel_filter", "spark_plug"],
            "oil_filter": ["air_filter", "engine_oil", "oil_pan_gasket"],
            "spark_plug": ["ignition_coil", "spark_plug_wire", "distributor_cap"],
            
            # Suspension relationships
            "shock_absorber": ["spring", "strut_mount", "bushing"],
            "spring": ["shock_absorber", "strut_mount", "bushing"],
            
            # Transmission relationships
            "clutch_kit": ["clutch_master_cylinder", "clutch_slave_cylinder", "clutch_cable"],
            "transmission_filter": ["transmission_fluid", "transmission_gasket"],
            
            # Electrical relationships
            "battery": ["alternator", "starter", "battery_cable"],
            "alternator": ["battery", "serpentine_belt", "voltage_regulator"],
            "starter": ["battery", "starter_solenoid", "ignition_switch"],
            
            # Cooling system relationships
            "radiator": ["thermostat", "coolant", "radiator_hose", "water_pump"],
            "water_pump": ["thermostat", "coolant", "timing_belt"],
            "thermostat": ["radiator", "coolant", "water_pump"],
        }

    def _load_maintenance_schedules(self) -> Dict[str, List[str]]:
        """Load maintenance schedule mappings."""
        return {
            "oil_change": ["oil_filter", "engine_oil", "oil_pan_gasket"],
            "brake_service": ["brake_pad", "brake_disc", "brake_fluid", "brake_sensor"],
            "air_filter_change": ["air_filter", "cabin_filter"],
            "spark_plug_replacement": ["spark_plug", "ignition_coil", "spark_plug_wire"],
            "timing_belt_service": ["timing_belt", "water_pump", "tensioner", "idler_pulley"],
            "suspension_service": ["shock_absorber", "spring", "strut_mount", "bushing"],
        }

    def _load_brand_compatibility(self) -> Dict[str, List[str]]:
        """Load brand compatibility mappings."""
        return {
            "Chery": ["JAC", "Brilliance", "BYD", "Geely"],
            "JAC": ["Chery", "Brilliance", "BYD"],
            "Brilliance": ["Chery", "JAC", "BYD"],
            "BYD": ["Chery", "JAC", "Brilliance", "Geely"],
            "Geely": ["Chery", "BYD", "Great Wall"],
            "Great Wall": ["Geely", "MG"],
            "MG": ["Great Wall", "Geely"],
        }

    async def get_recommendations(
        self,
        part_id: int,
        part_data: Dict[str, Any],
        user_profile: Optional[UserProfile] = None,
        recommendation_types: Optional[List[RecommendationType]] = None,
        limit: int = 5
    ) -> List[Recommendation]:
        """
        Get AI-powered recommendations for a part.
        
        Args:
            part_id: ID of the reference part
            part_data: Data about the reference part
            user_profile: Optional user profile for personalization
            recommendation_types: Types of recommendations to generate
            limit: Maximum number of recommendations
            
        Returns:
            List of recommendations sorted by relevance
        """
        if not part_data:
            return []

        if recommendation_types is None:
            recommendation_types = list(RecommendationType)

        all_recommendations = []

        # Generate different types of recommendations
        if RecommendationType.COMPLEMENTARY in recommendation_types:
            complementary = await self._get_complementary_recommendations(part_data, user_profile)
            all_recommendations.extend(complementary)

        if RecommendationType.ALTERNATIVE in recommendation_types:
            alternatives = await self._get_alternative_recommendations(part_data, user_profile)
            all_recommendations.extend(alternatives)

        if RecommendationType.MAINTENANCE in recommendation_types:
            maintenance = await self._get_maintenance_recommendations(part_data, user_profile)
            all_recommendations.extend(maintenance)

        if RecommendationType.UPGRADE in recommendation_types:
            upgrades = await self._get_upgrade_recommendations(part_data, user_profile)
            all_recommendations.extend(upgrades)

        if RecommendationType.FREQUENTLY_BOUGHT in recommendation_types:
            frequent = await self._get_frequently_bought_recommendations(part_data, user_profile)
            all_recommendations.extend(frequent)

        # Sort by recommendation score and remove duplicates
        unique_recommendations = self._deduplicate_recommendations(all_recommendations)
        unique_recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return unique_recommendations[:limit]

    async def _get_complementary_recommendations(
        self, 
        part_data: Dict[str, Any], 
        user_profile: Optional[UserProfile]
    ) -> List[Recommendation]:
        """Get complementary parts that work together."""
        recommendations = []
        part_category = part_data.get("category", "").lower()
        part_name = part_data.get("part_name", "").lower()
        
        # Find related parts based on category and name
        related_categories = self._find_related_categories(part_category, part_name)
        
        # This would typically query the database for parts in related categories
        # For now, we'll create mock recommendations
        for category in related_categories:
            # Mock recommendation data
            recommendation = Recommendation(
                part_id=999,  # Would be real part ID
                part_name=f"Related {category} part",
                brand_oem=part_data.get("brand_oem", ""),
                vehicle_make=part_data.get("vehicle_make", ""),
                vehicle_model=part_data.get("vehicle_model", ""),
                category=category,
                price=part_data.get("price", 0) * 0.8,  # Estimated price
                availability=True,
                recommendation_score=0.8,
                recommendation_type=RecommendationType.COMPLEMENTARY,
                reason=f"Works together with {part_data.get('part_name', 'this part')}",
                confidence=0.7,
                raw_data={}
            )
            recommendations.append(recommendation)
        
        return recommendations

    async def _get_alternative_recommendations(
        self, 
        part_data: Dict[str, Any], 
        user_profile: Optional[UserProfile]
    ) -> List[Recommendation]:
        """Get alternative brands or models for the same part."""
        recommendations = []
        current_brand = part_data.get("brand_oem", "")
        vehicle_make = part_data.get("vehicle_make", "")
        
        # Find compatible brands
        compatible_brands = self.brand_compatibility.get(vehicle_make, [])
        
        for brand in compatible_brands:
            if brand != current_brand:
                recommendation = Recommendation(
                    part_id=998,  # Would be real part ID
                    part_name=part_data.get("part_name", ""),
                    brand_oem=brand,
                    vehicle_make=vehicle_make,
                    vehicle_model=part_data.get("vehicle_model", ""),
                    category=part_data.get("category", ""),
                    price=part_data.get("price", 0) * 1.1,  # Estimated price
                    availability=True,
                    recommendation_score=0.7,
                    recommendation_type=RecommendationType.ALTERNATIVE,
                    reason=f"Alternative brand: {brand}",
                    confidence=0.6,
                    raw_data={}
                )
                recommendations.append(recommendation)
        
        return recommendations

    async def _get_maintenance_recommendations(
        self, 
        part_data: Dict[str, Any], 
        user_profile: Optional[UserProfile]
    ) -> List[Recommendation]:
        """Get maintenance-related recommendations."""
        recommendations = []
        part_category = part_data.get("category", "").lower()
        
        # Find maintenance tasks that include this part
        maintenance_tasks = []
        for task, parts in self.maintenance_schedules.items():
            if any(part in part_category for part in parts):
                maintenance_tasks.append(task)
        
        # Generate recommendations for other parts in the same maintenance task
        for task in maintenance_tasks:
            related_parts = self.maintenance_schedules[task]
            for part_type in related_parts:
                if part_type not in part_category:
                    recommendation = Recommendation(
                        part_id=997,  # Would be real part ID
                        part_name=f"Maintenance {part_type}",
                        brand_oem=part_data.get("brand_oem", ""),
                        vehicle_make=part_data.get("vehicle_make", ""),
                        vehicle_model=part_data.get("vehicle_model", ""),
                        category=part_type,
                        price=part_data.get("price", 0) * 0.5,  # Estimated price
                        availability=True,
                        recommendation_score=0.6,
                        recommendation_type=RecommendationType.MAINTENANCE,
                        reason=f"Recommended for {task}",
                        confidence=0.5,
                        raw_data={}
                    )
                    recommendations.append(recommendation)
        
        return recommendations

    async def _get_upgrade_recommendations(
        self, 
        part_data: Dict[str, Any], 
        user_profile: Optional[UserProfile]
    ) -> List[Recommendation]:
        """Get upgrade recommendations."""
        recommendations = []
        part_category = part_data.get("category", "").lower()
        current_price = part_data.get("price", 0)
        
        # Generate upgrade recommendations (higher quality/price parts)
        upgrade_categories = {
            "brake_pad": "performance_brake_pad",
            "air_filter": "high_flow_air_filter",
            "spark_plug": "iridium_spark_plug",
            "shock_absorber": "performance_shock_absorber",
        }
        
        if part_category in upgrade_categories:
            upgrade_category = upgrade_categories[part_category]
            recommendation = Recommendation(
                part_id=996,  # Would be real part ID
                part_name=f"Performance {part_data.get('part_name', '')}",
                brand_oem=part_data.get("brand_oem", ""),
                vehicle_make=part_data.get("vehicle_make", ""),
                vehicle_model=part_data.get("vehicle_model", ""),
                category=upgrade_category,
                price=current_price * 1.5,  # Higher price for upgrade
                availability=True,
                recommendation_score=0.5,
                recommendation_type=RecommendationType.UPGRADE,
                reason="Performance upgrade option",
                confidence=0.4,
                raw_data={}
            )
            recommendations.append(recommendation)
        
        return recommendations

    async def _get_frequently_bought_recommendations(
        self, 
        part_data: Dict[str, Any], 
        user_profile: Optional[UserProfile]
    ) -> List[Recommendation]:
        """Get frequently bought together recommendations."""
        recommendations = []
        
        # This would typically use purchase history data
        # For now, we'll use static popular combinations
        popular_combinations = {
            "brake_pad": ["brake_disc", "brake_fluid"],
            "air_filter": ["oil_filter", "cabin_filter"],
            "spark_plug": ["ignition_coil", "spark_plug_wire"],
        }
        
        part_category = part_data.get("category", "").lower()
        if part_category in popular_combinations:
            for related_part in popular_combinations[part_category]:
                recommendation = Recommendation(
                    part_id=995,  # Would be real part ID
                    part_name=f"Popular {related_part}",
                    brand_oem=part_data.get("brand_oem", ""),
                    vehicle_make=part_data.get("vehicle_make", ""),
                    vehicle_model=part_data.get("vehicle_model", ""),
                    category=related_part,
                    price=part_data.get("price", 0) * 0.7,  # Estimated price
                    availability=True,
                    recommendation_score=0.4,
                    recommendation_type=RecommendationType.FREQUENTLY_BOUGHT,
                    reason="Frequently bought together",
                    confidence=0.3,
                    raw_data={}
                )
                recommendations.append(recommendation)
        
        return recommendations

    def _find_related_categories(self, category: str, part_name: str) -> List[str]:
        """Find related categories based on part relationships."""
        related = []
        
        # Check direct relationships
        for part_type, related_parts in self.part_relationships.items():
            if part_type in category or part_type in part_name:
                related.extend(related_parts)
        
        # Check reverse relationships
        for part_type, related_parts in self.part_relationships.items():
            if category in related_parts or part_name in related_parts:
                related.append(part_type)
        
        return list(set(related))

    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Remove duplicate recommendations based on part_id."""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.part_id not in seen:
                seen.add(rec.part_id)
                unique_recommendations.append(rec)
            else:
                # If duplicate found, keep the one with higher score
                for i, existing in enumerate(unique_recommendations):
                    if existing.part_id == rec.part_id and rec.recommendation_score > existing.recommendation_score:
                        unique_recommendations[i] = rec
                        break
        
        return unique_recommendations

    def update_user_profile(
        self, 
        user_profile: UserProfile, 
        purchase: Dict[str, Any]
    ) -> UserProfile:
        """Update user profile with new purchase data."""
        user_profile.purchase_history.append(purchase)
        
        # Update preferences based on purchase history
        categories = [p.get("category", "") for p in user_profile.purchase_history]
        category_counts = Counter(categories)
        user_profile.preferences["favorite_categories"] = dict(category_counts.most_common(5))
        
        # Update brand preferences
        brands = [p.get("brand_oem", "") for p in user_profile.purchase_history]
        brand_counts = Counter(brands)
        user_profile.preferences["favorite_brands"] = dict(brand_counts.most_common(3))
        
        return user_profile

    def get_personalized_recommendations(
        self, 
        user_profile: UserProfile, 
        limit: int = 10
    ) -> List[Recommendation]:
        """Get personalized recommendations based on user profile."""
        recommendations = []
        
        # Get recommendations based on purchase history
        recent_purchases = user_profile.purchase_history[-5:]  # Last 5 purchases
        
        for purchase in recent_purchases:
            part_recommendations = self.get_recommendations(
                purchase.get("id", 0),
                purchase,
                user_profile,
                limit=2
            )
            recommendations.extend(part_recommendations)
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        return recommendations[:limit]

    def analyze_purchase_patterns(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze user purchase patterns for insights."""
        if not user_profile.purchase_history:
            return {"insights": [], "recommendations": []}
        
        # Analyze categories
        categories = [p.get("category", "") for p in user_profile.purchase_history]
        category_counts = Counter(categories)
        
        # Analyze brands
        brands = [p.get("brand_oem", "") for p in user_profile.purchase_history]
        brand_counts = Counter(brands)
        
        # Analyze price ranges
        prices = [p.get("price", 0) for p in user_profile.purchase_history if p.get("price")]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        insights = []
        
        if category_counts:
            most_common_category = category_counts.most_common(1)[0]
            insights.append(f"Most purchased category: {most_common_category[0]} ({most_common_category[1]} times)")
        
        if brand_counts:
            most_common_brand = brand_counts.most_common(1)[0]
            insights.append(f"Preferred brand: {most_common_brand[0]} ({most_common_brand[1]} times)")
        
        if avg_price > 0:
            insights.append(f"Average purchase price: ${avg_price:.2f}")
        
        return {
            "insights": insights,
            "category_distribution": dict(category_counts),
            "brand_distribution": dict(brand_counts),
            "average_price": avg_price,
            "total_purchases": len(user_profile.purchase_history)
        }
