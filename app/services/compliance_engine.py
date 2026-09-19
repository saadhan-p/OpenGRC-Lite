from app.models import db
from app.models.audit import AuditLog
from app.models.framework import Framework, Control, CheckDefinition, ControlCheckMapping
from app.models.host import AgentHost

SEVERITY_WEIGHTS = {
    'CRITICAL': 4.0,
    'HIGH': 3.0,
    'MEDIUM': 2.0,
    'LOW': 1.0
}


class ComplianceEngine:
    """
    Core GRC engine that calculates weighted compliance scores overall and per framework.
    """

    @staticmethod
    def get_latest_check_results():
        """
        Retrieves the latest audit check result for each host and control check.
        Returns a dictionary mapping (hostname, check_id) -> status string ('PASS', 'FAIL', 'WARNING').
        """
        all_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
        latest_results = {}
        for log in all_logs:
            key = (log.hostname, log.control_id)
            if key not in latest_results:
                latest_results[key] = log.status
        return latest_results

    @classmethod
    def calculate_overall_summary(cls):
        """Calculates global weighted score and multi-framework score breakdowns."""
        latest_results = cls.get_latest_check_results()
        total_hosts = AgentHost.query.count()
        check_defs = CheckDefinition.query.all()

        total_weight = 0.0
        passed_weight = 0.0
        passed_count = 0
        failed_count = 0

        # Overall weighted calculation
        for (hostname, check_id), status in latest_results.items():
            check_def = CheckDefinition.query.filter_by(check_id=check_id).first()
            weight = SEVERITY_WEIGHTS.get(check_def.severity, 2.0) if check_def else 2.0
            
            total_weight += weight
            if status == 'PASS':
                passed_weight += weight
                passed_count += 1
            elif status in ('FAIL', 'WARNING'):
                failed_count += 1

        overall_score = 100.0
        if total_weight > 0:
            overall_score = round((passed_weight / total_weight) * 100, 1)

        # Framework-specific breakdown calculation
        frameworks = Framework.query.all()
        framework_breakdown = {}

        for fw in frameworks:
            fw_total_weight = 0.0
            fw_passed_weight = 0.0
            fw_passed_cnt = 0
            fw_total_cnt = 0

            for control in fw.controls:
                for mapping in control.mappings:
                    check_id = mapping.check_definition.check_id
                    weight = SEVERITY_WEIGHTS.get(mapping.check_definition.severity, 2.0)

                    # Check latest host results for this mapped check
                    for (h_name, c_id), status in latest_results.items():
                        if c_id == check_id or check_id in c_id:
                            fw_total_cnt += 1
                            fw_total_weight += weight
                            if status == 'PASS':
                                fw_passed_weight += weight
                                fw_passed_cnt += 1

            fw_score = 100.0
            if fw_total_weight > 0:
                fw_score = round((fw_passed_weight / fw_total_weight) * 100, 1)

            framework_breakdown[fw.code] = {
                "name": fw.name,
                "version": fw.version,
                "score": fw_score,
                "passed_checks": fw_passed_cnt,
                "total_checks": fw_total_cnt
            }

        return {
            "overall_score": overall_score,
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "total_enrolled_hosts": total_hosts,
            "framework_breakdown": framework_breakdown
        }
