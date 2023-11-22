import re
import xml.etree.ElementTree as ET
from typing import Any


class Utility:
    @staticmethod
    def parse_confirmation_request(xml: str) -> dict:
        """Parse the Safaricom/Broker 'confirm request' XML string
        to a python dictionary object."""
        result: dict[str, str | Any] = {}
        metadata: list = []
        for node in ET.fromstring(xml)[0][0]:
            if node.tag.lower() == "kycinfo":
                metadata.append({child.tag: child.text for child in node if child.text})
                continue
            result.update({node.tag: node.text})
        if metadata:
            result.update({"KYCInfo": metadata})  # TODO: get fullname:(
        return result

    @staticmethod
    def validate_mobile_number(mobile_number: str) -> re.Match[str] | None:
        """Check if the given mobile number is a valid Safaricom mobile number."""
        pattern = re.compile(r"^(254|0)?[17]\d{8}$")
        return pattern.match(mobile_number)

    @staticmethod
    def rewrite_mobile_number(mobile_number: str) -> str:
        """(re)Write mobile number, prefixing it with '254' (country code)."""
        return (
            f"254{mobile_number[-9:]}"
            if Utility.validate_mobile_number(mobile_number)
            else ""
        )
