class IdGenerator:
    """Deterministic ID generator conforming to platform requirements."""

    @staticmethod
    def plant_id(index: int) -> str:
        return f"PLN-{index:03d}"

    @staticmethod
    def machine_id(index: int) -> str:
        return f"MCH-{index:03d}"

    @staticmethod
    def safety_zone_id(plant_id: str, index: int) -> str:
        return f"SAFE-{plant_id}-{index:03d}"

    @staticmethod
    def interlock_id(machine_id: str, index: int) -> str:
        return f"ITL-{machine_id}-{index:03d}"

    @staticmethod
    def alarm_definition_id(index: int) -> str:
        return f"DEF-{index:03d}"

    @staticmethod
    def alarm_event_id(machine_id: str, seq: int) -> str:
        return f"ALM-{machine_id}-{seq:06d}"

    @staticmethod
    def operator_shift_id(seq: int) -> str:
        return f"SHF-{seq:06d}"

    @staticmethod
    def incident_id(year: int, seq: int) -> str:
        return f"INC-{year}-{seq:06d}"

    @staticmethod
    def acknowledgement_id(alarm_id: str, seq: int = 1) -> str:
        return f"ACK-{alarm_id}-{seq:02d}"

    @staticmethod
    def corrective_action_id(incident_id: str, seq: int = 1) -> str:
        return f"ACT-{incident_id}-{seq:02d}"

    @staticmethod
    def anomaly_id(year: int, seq: int) -> str:
        return f"ANM-{year}-{seq:06d}"
