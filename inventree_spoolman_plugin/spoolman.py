"""Sample implementation for ActionMixin."""

import inspect, json, logging

from plugin import InvenTreePlugin
from plugin.mixins import ActionMixin, APICallMixin, SettingsMixin, EventMixin
from company.models import Company, SupplierPriceBreak
from part.models import (
    Part,
    SupplierPart,
    PartCategory,
    PartParameterTemplate,
    PartParameter,
)
from stock.models import StockItem

logger = logging.getLogger("spoolmanplugin")


class SpoolmanPlugin(ActionMixin, APICallMixin, SettingsMixin, InvenTreePlugin):
    """An action plugin which offers variuous integrations with Spoolman."""

    NAME = "SpoolmanPlugin"
    SLUG = "spoolmanplugin"
    TITLE = "Spoolman Integration"
    DESCRIPTION = ("Spoolman integration for InvenTree")
    VERSION = "0.2"
    AUTHOR = "Jackymancs4"
    LICENSE = "MIT"

    SETTINGS = {
        "API_URL": {
            "name": "External URL",
            "description": "Where is your API located?",
            "required": True,
        },
        "FILAMENT_CATEGORY_ID": {
            "name": "Category for filament parts",
            "description": "Generic description",
            "model": "part.partcategory",
        },
        "MATERIAL_PART_PARAMETER_ID": {
            "name": "Material Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "DENSITY_PART_PARAMETER_ID": {
            "name": "Density Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "DIAMETER_PART_PARAMETER_ID": {
            "name": "Diameter Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "SPOOL_WEIGHT_PART_PARAMETER_ID": {
            "name": "Spool weight Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "MIN_EXTRUDER_TEMP_PART_PARAMETER_ID": {
            "name": "Min extruder temp Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "MAX_EXTRUDER_TEMP_PART_PARAMETER_ID": {
            "name": "Max extruder temp Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "MIN_BED_TEMP_PART_PARAMETER_ID": {
            "name": "Min bed temp Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "MAX_BED_TEMP_PART_PARAMETER_ID": {
            "name": "Max bed temp Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
        "COLOR_PART_PARAMETER_ID": {
            "name": "Hexadecimal Color Part Parameter",
            "description": "Generic description",
            "model": "part.partparametertemplate",
        },
    }

    API_URL_SETTING = "API_URL"

    result = {}

    @property
    def api_url(self):
        """Base url path."""
        return f"{self.get_setting(self.API_URL_SETTING)}"

    def create_part_parameters(self):
        """Add all the part parameters not already set through the settings"""

        parameter_template_pk = False
        parameter_template = None

        parameter_template_pk = self.get_setting("MATERIAL_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Material"
            )[0]
            self.set_setting("MATERIAL_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("DENSITY_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Density", units="gram / centimeter ** 3"
            )[0]
            self.set_setting("DENSITY_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("DIAMETER_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Diameter", units="mm"
            )[0]
            self.set_setting("DIAMETER_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("SPOOL_WEIGHT_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Spool Weight", units="g"
            )[0]
            self.set_setting("SPOOL_WEIGHT_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("MIN_EXTRUDER_TEMP_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Min Ext temp", units="degC"
            )[0]
            self.set_setting(
                "MIN_EXTRUDER_TEMP_PART_PARAMETER_ID", parameter_template.pk
            )

        parameter_template_pk = self.get_setting("MAX_EXTRUDER_TEMP_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Max Ext temp", units="degC"
            )[0]
            self.set_setting(
                "MAX_EXTRUDER_TEMP_PART_PARAMETER_ID", parameter_template.pk
            )

        parameter_template_pk = self.get_setting("MIN_BED_TEMP_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Min Bed temp", units="degC"
            )[0]
            self.set_setting("MIN_BED_TEMP_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("MAX_BED_TEMP_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Max Bed temp", units="degC"
            )[0]
            self.set_setting("MAX_BED_TEMP_PART_PARAMETER_ID", parameter_template.pk)

        parameter_template_pk = self.get_setting("COLOR_PART_PARAMETER_ID")

        if not parameter_template_pk:
            parameter_template = PartParameterTemplate.objects.get_or_create(
                name="Hex Color"
            )[0]
            self.set_setting("COLOR_PART_PARAMETER_ID", parameter_template.pk)

    def get_supplier(self, spool:dict) -> (Company | None):
        """_summary_

        Args:
            spool (_type_): _description_
        """
        supplier_name = None
        supplier = None

        # Get the supplier if there is one
        if "vendor" in spool["filament"]:

            vendor_id = spool["filament"]["vendor"]["id"]

            supplier = Company.objects.filter(metadata__spoolman_id=vendor_id).first()

            if not supplier:
                supplier_name = spool["filament"]["vendor"]["name"]
                supplier = Company.objects.get_or_create(
                    name=supplier_name,
                )[0]

                supplier.metadata["spoolman_id"] = vendor_id

                supplier.notes = (
                    spool["filament"]["vendor"]["comment"]
                    if "comment" in spool["filament"]["vendor"]
                    else ""
                )

                supplier.save()

        return supplier

    def upsert_parameter(self, spool, part, setting_key, filament_key):
        """_summary_

        Args:
            spool (dict): _description_
            part (Part): _description_
            setting_key (str): _description_
            filament_key (str): _description_
        """

        parameter_template_pk = self.get_setting(setting_key)

        if filament_key in spool["filament"] and parameter_template_pk:

            parameter_template = PartParameterTemplate.objects.get(
                pk=parameter_template_pk
            )

            PartParameter.objects.get_or_create(
                part=part,
                template=parameter_template,
                data=spool["filament"][filament_key],
            )[0]

    def process_spool(self, spool, category):
        """Process a single spool object

        Args:
            spool (dict): _description_
            category (PartCategory): _description_
        """
        
        supplier = self.get_supplier(spool)

        part = Part.objects.filter(
            metadata__contains=[{"spoolman_id": spool["filament"]["id"]}]
        ).first()

        if not part:
            logger.debug("Filament not found by ID: " + str(spool["filament"]["id"]))

            if supplier:
                part_name = supplier.name + " " + spool["filament"]["name"]
            else:
                part_name = spool["filament"]["name"]

            part = Part.objects.get_or_create(
                name=part_name,
                category=category,
            )[0]

            part.metadata["spoolman_id"] = spool["filament"]["id"]

            part.notes = (
                spool["filament"]["comment"] if "comment" in spool["filament"] else ""
            )
            part.units = "g"
            part.component = True

            part.save()

        self.upsert_parameter(spool, part, "MATERIAL_PART_PARAMETER_ID", "material")
        self.upsert_parameter(spool, part, "DENSITY_PART_PARAMETER_ID", "density")
        self.upsert_parameter(spool, part, "DIAMETER_PART_PARAMETER_ID", "diameter")
        self.upsert_parameter(spool, part, "SPOOL_WEIGHT_PART_PARAMETER_ID", "spool_weight")
        self.upsert_parameter(spool, part, "MIN_EXTRUDER_TEMP_PART_PARAMETER_ID", "settings_extruder_temp")
        self.upsert_parameter(spool, part, "MAX_EXTRUDER_TEMP_PART_PARAMETER_ID", "settings_extruder_temp")
        self.upsert_parameter(spool, part, "MIN_BED_TEMP_PART_PARAMETER_ID", "settings_bed_temp")
        self.upsert_parameter(spool, part, "MAX_BED_TEMP_PART_PARAMETER_ID", "settings_bed_temp")
        self.upsert_parameter(spool, part, "COLOR_PART_PARAMETER_ID", "color_hex")

        # link filament to supplier
        if supplier:
            supplier_part = SupplierPart.objects.get_or_create(
                part=part,
                supplier=supplier,
            )[0]

            supplier_part.SKU = (
                spool["filament"]["article_number"]
                if "article_number" in spool["filament"]
                else spool["filament"]["id"]
            )
            supplier_part.pack_quantity = str(spool["filament"]["weight"])

            supplier_part.save()

            if "price" in spool["filament"]:

                supplier_price_break = SupplierPriceBreak.objects.get_or_create(
                    part=supplier_part,
                    quantity=1,
                )[0]

                supplier_price_break.price = str(spool["filament"]["price"])

                supplier_price_break.save()

        # Retrieve or create stock
        stock = StockItem.objects.filter(metadata__spoolman_id=spool["id"]).first()

        if not stock:
            stock = StockItem.objects.get_or_create(part=part, batch=spool["lot_nr"])[0]
            stock.metadata["spoolman_id"] = spool["id"]

        stock.updateQuantity(spool["remaining_weight"])

    def clear_metadata(self):
        """_summary_
        """
        parts = Part.objects.filter(metadata__icontains="spoolman_id")

        for part in parts:
            logger.debug("Spoolman part found: " + str(part.pk))

            part.metadata.pop("spoolman_id")
            part.save()

    def perform_action(self, user=None, data=None):
        """_summary_

        Args:
            user (_type_, optional): _description_. Defaults to None.
            data (_type_, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_
            NotImplementedError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        initial_response = self.api_call("api/v1/info", simple_response=False)

        if initial_response.status_code != 200:
            self.result = {"error"}
            return False

        command = data.get("command")

        if command == "import_all":

            filaments_response = self.api_call("api/v1/spool")

            category = None

            if category_pk := self.get_setting("FILAMENT_CATEGORY_ID"):
                try:
                    category = PartCategory.objects.get(pk=category_pk)
                except PartCategory.DoesNotExist:
                    category = None

            # Per ogni spool
            for spool in filaments_response:
                self.process_spool(spool, category)

                print("Imported spool " + str(spool["id"]))

        elif command == "import_quantity":
            raise NotImplementedError

        elif command == "export_all":
            raise NotImplementedError

        elif command == "export_quantity":
            raise NotImplementedError

        elif command == "create_part_parameter_templates":
            self.create_part_parameters()

        elif command == "clear_metadata":
            self.clear_metadata()

        else:
            self.result = {"error"}
