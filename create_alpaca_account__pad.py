https://alpaca.markets/docs/api-references/broker-api/accounts/accounts/#request

def create_alpaca_account():
    return {
    "enabled_assets": ["us_equity", "crypto"],
    "contact": {
        "email_address": "cool_alpaca@example.com",
        "phone_number": "555-666-7788",
        "street_address": ["20 N San Mateo Dr"],
        "unit": "Apt 1A",
        "city": "San Mateo",
        "state": "CA",
        "postal_code": "94401",
        "country": "USA"
    },
    "identity": {
        "given_name": "John",
        "middle_name": "Smith",
        "family_name": "Doe",
        "date_of_birth": "1990-01-01",
        "tax_id": "666-55-4321",
        "tax_id_type": "USA_SSN",
        "country_of_citizenship": "USA",
        "country_of_birth": "USA",
        "country_of_tax_residence": "USA",
        "funding_source": ["employment_income"]
    },
    "disclosures": {
        "is_control_person": false,
        "is_affiliated_exchange_or_finra": true,
        "is_politically_exposed": false,
        "immediate_family_exposed": false,
        "context": [
        {
            "context_type": "AFFILIATE_FIRM",
            "company_name": "Finra",
            "company_street_address": ["1735 K Street, NW"],
            "company_city": "Washington",
            "company_state": "DC",
            "company_country": "USA",
            "company_compliance_email": "compliance@finra.org"
        }
        ]
    },
    "agreements": [
        {
        "agreement": "customer_agreement",
        "signed_at": "2020-09-11T18:13:44Z",
        "ip_address": "185.13.21.99",
        "revision": "19.2022.02"
        },
        {
        "agreement": "crypto_agreement",
        "signed_at": "2020-09-11T18:13:44Z",
        "ip_address": "185.13.21.99",
        "revision": "04.2021.10"
        }
    ],
    "documents": [
        {
        "document_type": "identity_verification",
        "document_sub_type": "passport",
        "content": "/9j/Cg==",
        "mime_type": "image/jpeg"
        }
    ],
    "trusted_contact": {
        "given_name": "Jane",
        "family_name": "Doe",
        "email_address": "jane.doe@example.com"
    }
    }


sample response{
    "id": "de9d0029-e0a0-4a2f-b630-265a32dd00c4",
    "account_number": "808333970",
    "status": "SUBMITTED",
    "crypto_status": "SUBMITTED",
    "currency": "USD",
    "last_equity": "0",
    "created_at": "2022-08-16T20:36:07.514367Z",
    "contact": {
        "email_address": "cool_alpacaa@example.com",
        "phone_number": "555-666-7788",
        "street_address": [
            "20 N San Mateo Dr"
        ],
        "unit": "Apt 1A",
        "city": "San Mateo",
        "state": "CA",
        "postal_code": "94401"
    },
    "identity": {
        "given_name": "John",
        "family_name": "Doe",
        "middle_name": "Smith",
        "date_of_birth": "1990-01-01",
        "tax_id_type": "USA_SSN",
        "country_of_citizenship": "USA",
        "country_of_birth": "USA",
        "country_of_tax_residence": "USA",
        "funding_source": [
            "employment_income"
        ],
        "visa_type": null,
        "visa_expiration_date": null,
        "date_of_departure_from_usa": null,
        "permanent_resident": null
    },
    "disclosures": {
        "is_control_person": false,
        "is_affiliated_exchange_or_finra": true,
        "is_politically_exposed": false,
        "immediate_family_exposed": false,
        "is_discretionary": false
    },
    "agreements": [
      {
        "agreement": "customer_agreement",
        "signed_at": "2020-09-11T18:13:44Z",
        "ip_address": "185.13.21.99",
        "revision": "19.2022.02"
      },
      {
        "agreement": "crypto_agreement",
        "signed_at": "2020-09-11T18:13:44Z",
        "ip_address": "185.13.21.99",
        "revision": "04.2021.10"
      }
    ],
    "trusted_contact": {
        "given_name": "Jane",
        "family_name": "Doe",
        "email_address": "jane.doe@example.com"
    },
    "account_type": "trading",
    "trading_configurations": null,
    "enabled_assets": [
        "us_equity",
        "crypto"
    ]
}