BROKER_VALIDATION_RESPONSE_TEMPLATE: str = """
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:c2b="http://cps.huawei.com/cpsinterface/c2bpayment">
    <soapenv:Header/>
    <soapenv:Body>
        <c2b:C2BPaymentValidationResult>
            <ResultCode>{RESULT_CODE}</ResultCode>
            <ResultDesc>{RESULT_DESCRIPTION}</ResultDesc>
            <ThirdPartyTransactionID>{THIRD_PARTY_TRANSACTION_ID}</ThirdPartyTransactionID>
        </c2b:C2BPaymentValidationResult>
    </soapenv:Body>
</soapenv:Envelope>
"""


BROKER_CONFIRMATION_RESPONSE_TEMPLATE: str = """
<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:c2b="http://cps.huawei.com/cpsinterface/c2bpayment">
    <soapenv:Header/>
    <soapenv:Body>
        <c2b:C2BPaymentConfirmationResult>{MESSAGE}</c2b:C2BPaymentConfirmationResult>
    </soapenv:Body>
</soapenv:Envelope>
"""
