from app.connectors.factory import get_connector


class ConnectorService:

    @staticmethod
    def validate(
        source_type: str,
        config: dict,
    ) -> dict:

        try:
            connector = get_connector(
                source_type,
                config,
            )

            valid = connector.validate()

            if not valid:
                return {
                    "valid": False,
                    "message": "Data source is not accessible",
                }

            return {
                "valid": True,
                "message": "Data source is accessible",
            }

        except Exception as exc:
            return {
                "valid": False,
                "message": str(exc),
            }