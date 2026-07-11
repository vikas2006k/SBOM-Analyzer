from datetime import datetime, timedelta
import random
from app.database.connection import db
from app.models.library import Library
from app.models.dependency import Dependency
from app.models.maintenance import MaintenanceRecord
from app.utils.logger import Logger

logger = Logger.get_logger('app')

# Predefined realistic metrics for common dependencies in mock data
MAINTENANCE_METRICS_DB = {
    "spring-boot-starter-web": {"days_ago": 15, "commits": 850, "issues": 12, "bus_factor": 18, "deprecated": False},
    "jackson-databind": {"days_ago": 45, "commits": 310, "issues": 48, "bus_factor": 6, "deprecated": False},
    "log4j-core": {"days_ago": 60, "commits": 120, "issues": 18, "bus_factor": 4, "deprecated": False},
    "jsonwebtoken": {"days_ago": 480, "commits": 2, "issues": 142, "bus_factor": 1, "deprecated": True},
    "requests": {"days_ago": 8, "commits": 280, "issues": 35, "bus_factor": 14, "deprecated": False},
    "urllib3": {"days_ago": 22, "commits": 140, "issues": 19, "bus_factor": 5, "deprecated": False},
    "express": {"days_ago": 180, "commits": 45, "issues": 94, "bus_factor": 3, "deprecated": False},
    "ms": {"days_ago": 320, "commits": 15, "issues": 8, "bus_factor": 2, "deprecated": False},
    "idna": {"days_ago": 150, "commits": 30, "issues": 5, "bus_factor": 2, "deprecated": False},
    "certifi": {"days_ago": 10, "commits": 90, "issues": 3, "bus_factor": 3, "deprecated": False}
}

class MaintenanceService:
    """Service auditing open-source repositories activity, updates frequency, and sustainability risk."""

    def __init__(self):
        pass

    def get_or_create_record(self, library):
        """Fetch or create maintenance metric logs for a library."""
        record = MaintenanceRecord.query.filter_by(library_id=library.id).first()
        if record:
            return record
            
        # Determine stats
        name = library.name.lower()
        if name in MAINTENANCE_METRICS_DB:
            stats = MAINTENANCE_METRICS_DB[name]
        else:
            # Generate deterministic but random-looking stats based on name hash
            seed = sum(ord(char) for char in name)
            random.seed(seed)
            stats = {
                "days_ago": random.randint(5, 730),
                "commits": random.randint(0, 400),
                "issues": random.randint(0, 150),
                "bus_factor": random.randint(1, 12),
                "deprecated": random.random() < 0.04 # 4% deprecation chance
            }
            
        last_updated_date = datetime.now() - timedelta(days=stats["days_ago"])
        
        record = MaintenanceRecord(
            library_id=library.id,
            last_updated=last_updated_date,
            commit_frequency_annual=stats["commits"],
            open_issues_count=stats["issues"],
            bus_factor=stats["bus_factor"],
            is_deprecated=stats["deprecated"]
        )
        db.session.add(record)
        db.session.commit()
        return record

    def calculate_score(self, record):
        """Calculate maintenance score (0-100) based on age, commits, issues, deprecation, and bus factor."""
        score = 100.0
        warnings = []
        
        # 1. Deprecation Penalty
        if record.is_deprecated:
            score -= 50.0
            warnings.append("Library is deprecated by the maintainers.")
            
        # 2. Repository Age / Stale Penalty
        age_days = (datetime.now() - record.last_updated).days
        if age_days > 730: # 2+ years
            score -= 25.0
            warnings.append(f"Repository is extremely stale. Last release was {age_days // 365} years ago ({record.last_updated.strftime('%Y-%m-%d')}).")
        elif age_days > 365: # 1+ years
            score -= 15.0
            warnings.append(f"Repository is stale. Last release was {age_days} days ago ({record.last_updated.strftime('%Y-%m-%d')}).")
            
        # 3. Bus Factor Risk
        if record.bus_factor == 1:
            score -= 20.0
            warnings.append("Critical Bus Factor of 1. Only a single contributor maintains this project.")
        elif record.bus_factor == 2:
            score -= 10.0
            warnings.append("Low Bus Factor of 2. Project lacks development sustainability.")
            
        # 4. Commit Frequency Penalty
        if record.commit_frequency_annual < 5:
            score -= 10.0
            warnings.append(f"Almost zero commits ({record.commit_frequency_annual}) in the past year. Repository is abandoned.")
        elif record.commit_frequency_annual < 20:
            score -= 5.0
            warnings.append(f"Low commit activity ({record.commit_frequency_annual} commits/year).")
            
        # 5. Open Issues Penalty
        if record.open_issues_count > 100:
            score -= 5.0
            warnings.append(f"High unresolved issue backlog ({record.open_issues_count} open issues).")
            
        score = max(0.0, min(100.0, score))
        
        # Determine Health category
        if score >= 80:
            health = "Healthy"
        elif score >= 50:
            health = "Medium Risk"
        else:
            health = "Critical Risk"
            
        return {
            "score": score,
            "health_level": health,
            "age_days": age_days,
            "warnings": warnings
        }

    def check_maintenance_health(self, application_id):
        """Retrieve maintenance score summaries for an application."""
        edges = Dependency.query.filter_by(application_id=application_id, is_deleted=False).all()
        libraries = {edge.child_library for edge in edges if edge.child_library}
        
        records_summary = []
        deprecated_count = 0
        abandoned_count = 0
        total_score = 0.0
        
        for lib in libraries:
            record = self.get_or_create_record(lib)
            analysis = self.calculate_score(record)
            
            if record.is_deprecated:
                deprecated_count += 1
            if (datetime.now() - record.last_updated).days > 365 or record.commit_frequency_annual < 5:
                abandoned_count += 1
                
            total_score += analysis["score"]
            records_summary.append({
                "library_id": lib.id,
                "library_name": lib.name,
                "library_version": lib.version,
                "last_release": record.last_updated.isoformat(),
                "age_days": analysis["age_days"],
                "commit_frequency_annual": record.commit_frequency_annual,
                "open_issues_count": record.open_issues_count,
                "bus_factor": record.bus_factor,
                "is_deprecated": record.is_deprecated,
                "maintenance_score": analysis["score"],
                "health_level": analysis["health_level"],
                "warnings": analysis["warnings"]
            })
            
        avg_score = (total_score / len(records_summary)) if records_summary else 100.0
        
        # Sort by maintenance score ascending (worst first)
        records_summary.sort(key=lambda x: x["maintenance_score"])
        
        return {
            "application_id": application_id,
            "average_maintenance_score": round(avg_score, 2),
            "deprecated_count": deprecated_count,
            "abandoned_count": abandoned_count,
            "dependencies": records_summary
        }
