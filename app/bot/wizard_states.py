"""Wizard state machine for guided part search flow."""

from aiogram.fsm.state import State, StatesGroup


class PartsWizard(StatesGroup):
    """Wizard states for guided part search flow."""

    # Initial states
    start = State()
    brand_selection = State()
    model_selection = State()
    year_trim_selection = State()
    category_selection = State()
    part_selection = State()
    confirmation = State()
    contact_capture = State()
    completed = State()

    # Alternative flows
    quick_search = State()  # For expert users
    bulk_search = State()  # For multiple parts


class WizardData:
    """Data structure for wizard session."""

    def __init__(self):
        self.vehicle_data = {}
        self.part_data = {}
        self.contact_data = {}
        self.search_results = []
        self.selected_parts = []

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            "vehicle_data": self.vehicle_data,
            "part_data": self.part_data,
            "contact_data": self.contact_data,
            "search_results": self.search_results,
            "selected_parts": self.selected_parts,
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        wizard_data = cls()
        wizard_data.vehicle_data = data.get("vehicle_data", {})
        wizard_data.part_data = data.get("part_data", {})
        wizard_data.contact_data = data.get("contact_data", {})
        wizard_data.search_results = data.get("search_results", [])
        wizard_data.selected_parts = data.get("selected_parts", [])
        return wizard_data
