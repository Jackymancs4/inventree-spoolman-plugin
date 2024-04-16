"""Sample implementation for ActionMixin."""

from plugin import InvenTreePlugin
from plugin.mixins import ActionMixin, APICallMixin, SettingsMixin, EventMixin
from company.models import Company, SupplierPriceBreak
from part.models import Part, SupplierPart, PartCategory, PartParameterTemplate, PartParameter
from stock.models import StockItem

class SpoolmanPlugin(ActionMixin, APICallMixin, SettingsMixin, InvenTreePlugin):
    """An EXTREMELY simple action plugin which demonstrates the capability of the ActionMixin class."""

    NAME = 'SpoolmanPlugin'
    SLUG = 'spoolman'
    ACTION_NAME = 'spoolman'

    SETTINGS = {
        'API_URL': {
            'name': 'External URL',
            'description': 'Where is your API located?',
            'default': 'reqres.in',
        },
    }

    API_URL_SETTING = 'API_URL'

    result = {}

    @property
    def api_url(self):
        """Base url path."""
        return f'{self.get_setting(self.API_URL_SETTING)}'

    def perform_action(self, user=None, data=None):
        """Sample method."""
        print('Action plugin in action!')

        print(self.api_url)

        initial_response = self.api_call('api/v1/info', simple_response=False)

        if initial_response.status_code != 200:
            self.result = {'error'}
            return False
        
        filaments_response = self.api_call('api/v1/spool')

        # Ottieni la categoria
        category = PartCategory.objects.get_or_create(name="Filamenti")[0]

        materialParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Materiale")[0]

        densityParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Densità", units="gram / centimeter ** 3")[0]

        diameterParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Diametro", units="mm")[0]

        spool_weight_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Peso bobina", units="g")[0]

        min_extruder_temp_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Min Ext temp", units="degC")[0]

        max_extruder_temp_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Max Ext temp", units="degC")[0]

        min_bed_temp_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Min Bed temp", units="degC")[0]

        max_bed_temp_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Max Bed temp", units="degC")[0]

        color_hex_ParameterTemplate = PartParameterTemplate.objects.get_or_create(name="Colore esadecimale")[0]

        # Per ogni spool
        for spool in filaments_response:

            supplier_name = None
            supplier = None

            # ottieni il supplier
            if "vendor" in spool["filament"]: 
                supplier_name = spool["filament"]["vendor"]["name"]
                supplier=Company.objects.get_or_create(
                    name=supplier_name,
                )[0]

                supplier.notes = spool["filament"]["vendor"]["comment"] if "comment" in spool["filament"]["vendor"] else ""

                supplier.save()

            # se non presente lo crei

            # ottieni il filamento
            part_name = spool["filament"]["name"]
            part=Part.objects.get_or_create(
                name=part_name, 
                category=category,
            )[0]

            part.notes = spool["filament"]["comment"] if "comment" in spool["filament"] else ""
            part.units = "g"
            part.component = True

            part.save()

            PartParameter.objects.get_or_create(
                part = part, 
                template = materialParameterTemplate, 
                data = spool["filament"]["material"]
            )[0]

            if "density" in spool["filament"]: 

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = densityParameterTemplate, 
                    data = spool["filament"]["density"]
                )[0]

            if "diameter" in spool["filament"]: 

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = diameterParameterTemplate, 
                    data = spool["filament"]["diameter"]
                )[0]

            if "spool_weight" in spool["filament"]: 
                PartParameter.objects.get_or_create(
                    part = part, 
                    template = spool_weight_ParameterTemplate, 
                    data = spool["filament"]["spool_weight"]
                )[0]

            if "settings_extruder_temp" in spool["filament"]: 

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = min_extruder_temp_ParameterTemplate, 
                    data = spool["filament"]["settings_extruder_temp"]
                )[0]

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = max_extruder_temp_ParameterTemplate, 
                    data = spool["filament"]["settings_extruder_temp"]
                )[0]

            if "settings_bed_temp" in spool["filament"]: 
                PartParameter.objects.get_or_create(
                    part = part, 
                    template = min_bed_temp_ParameterTemplate, 
                    data = spool["filament"]["settings_bed_temp"]
                )[0]

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = max_bed_temp_ParameterTemplate, 
                    data = spool["filament"]["settings_bed_temp"]
                )[0]

            if "color_hex" in spool["filament"]: 

                PartParameter.objects.get_or_create(
                    part = part, 
                    template = color_hex_ParameterTemplate, 
                    data = spool["filament"]["color_hex"]
                )[0]

            # se non presente lo crei

            # colleghi il filamento al supplier
            if supplier != None:    
                supplier_part = SupplierPart.objects.get_or_create(
                    part = part, 
                    supplier = supplier,
                )[0]

                supplier_part.SKU = spool["filament"]["article_number"] if "article_number" in spool["filament"] else spool["filament"]["id"]
                supplier_part.pack_quantity = str(spool["filament"]["weight"])

                supplier_part.save()

                if "price" in spool["filament"]:

                    supplier_price_break = SupplierPriceBreak.objects.get_or_create(
                        part = supplier_part,
                        quantity = 1,
                    )[0]

                    supplier_price_break.price = str(spool["filament"]["price"])

                    supplier_price_break.save()

            # crei la giacenza
            stock = StockItem.objects.get_or_create(
                part=part, 
                batch = spool["lot_nr"]
            )[0]

            stock.updateQuantity(spool["remaining_weight"])

            print("Imported spool " + str(spool["id"]))

        self.result = filaments_response

    def get_info(self, user, data=None):
        """Sample method."""
        return {'user': user.username, 'hello': 'world'}

    def get_result(self, user=None, data=None):
        """Sample method."""
        return self.result
