from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings


class QgisConverterModule:
    display_value_extractor: "DisplayValueExtractor"
    properties_extractor: "PropertiesExtractor"
    conversion_settings: QgisConversionSettings

    def __init__(
        self, display_value_extractor, properties_extractor, conversion_settings
    ):
        self.display_value_extractor = display_value_extractor or None
        self.properties_extractor = display_value_extractor or None
        self.conversion_settings = conversion_settings
