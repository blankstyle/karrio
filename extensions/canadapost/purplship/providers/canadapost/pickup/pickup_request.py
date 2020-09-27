from typing import Tuple, List, Union
from functools import partial
from pycanadapost.pickuprequest import (
    PickupRequestDetailsType,
    PickupRequestUpdateDetailsType,
    PickupLocationType,
    AlternateAddressType,
    ContactInfoType,
    LocationDetailsType,
    ItemsCharacteristicsType,
    PickupTimesType,
    OnDemandPickupTimeType,
    PickupRequestInfoType,
    PickupRequestPriceType,
    PickupRequestHeaderType,
    PickupTypeType as PickupType
)
from purplship.core.utils import Serializable, export, Element, concat_str, build, format_date, decimal
from purplship.core.models import PickupRequest, PickupDetails, Message, ChargeDetails
from purplship.core.units import Packages
from purplship.providers.canadapost.units import PackagePresets
from purplship.providers.canadapost.utils import Settings
from purplship.providers.canadapost.error import parse_error_response

PickupRequestDetails = Union[PickupRequestDetailsType, PickupRequestUpdateDetailsType]


def parse_pickup_response(response: Element, settings: Settings) -> Tuple[PickupDetails, List[Message]]:
    pickup = (
        _extract_pickup_details(response, settings)
        if len(response.xpath(".//*[local-name() = $name]", name="pickup-request-info")) > 0
        else None
    )
    return pickup, parse_error_response(response, settings)


def _extract_pickup_details(response: Element, settings: Settings) -> PickupDetails:
    pickup_info = next(
        build(PickupRequestInfoType, elt) for elt in
        response.xpath(".//*[local-name() = $name]", name="pickup-request-info")
    )
    header: PickupRequestHeaderType = pickup_info.pickup_request_header
    price: PickupRequestPriceType = pickup_info.pickup_request_price

    price_amount = sum([
        decimal(price.hst_amount or 0.0),
        decimal(price.gst_amount or 0.0),
        decimal(price.due_amount or 0.0)
    ], 0.0)

    return PickupDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        confirmation_number=header.request_id,
        pickup_date=format_date(header.next_pickup_date),
        pickup_charge=ChargeDetails(name="Pickup fees", amount=decimal(price_amount), currency="CAD")
    )


def pickup_request(payload: PickupRequest, settings: Settings, update: bool = False) -> Serializable[PickupRequestDetails]:
    """
    pickup_request create a serializable typed PickupRequestDetailsType

    Options:
        - five_ton_flag
        - loading_dock_flag

    :param update: bool
    :param payload: PickupRequest
    :param settings: Settings
    :return: Serializable[PickupRequest]
    """
    packages = Packages(payload.parcels, PackagePresets, required=["weight"])
    heavy = any([p for p in packages if p.weight.KG > 23])
    location_details = dict(
        instruction=payload.instruction,
        five_ton_flag=payload.options.get('five_ton_flag'),
        loading_dock_flag=payload.options.get('loading_dock_flag')
    )
    address = dict(
        company=payload.address.company_name,
        address_line_1=concat_str(payload.address.address_line1, payload.address.address_line2, join=True),
        city=payload.address.city,
        province=payload.address.state_code,
        postal_code=payload.address.postal_code
    )
    contact = dict(
        contact_name=payload.address.person_name,
        email=payload.address.email,
        contact_phone=payload.address.phone_number,
    )

    request = PickupRequestDetailsType(
        customer_request_id=settings.customer_number,
        pickup_type=PickupType.ON_DEMAND.value,
        pickup_location=PickupLocationType(
            business_address_flag=(not payload.address.residential),
            alternate_address=AlternateAddressType(
                company=address['company'],
                address_line_1=address['address_line_1'],
                city=address['city'],
                province=address['province'],
                postal_code=address['postal_code'],
            ) if any(address.values()) else None
        ),
        contact_info=ContactInfoType(
            contact_name=contact['contact_name'],
            email=contact['email'],
            contact_phone=contact['contact_phone'],
            telephone_ext=None,
            receive_email_updates_flag=(contact['email'] is not None)
        ) if any(contact.values()) else None,
        location_details=LocationDetailsType(
            five_ton_flag=location_details['five_ton_flag'],
            loading_dock_flag=location_details['loading_dock_flag'],
            pickup_instructions=location_details['instruction']
        ) if any(location_details.values()) else None,
        items_characteristics=ItemsCharacteristicsType(
            pww_flag=None,
            priority_flag=None,
            returns_flag=None,
            heavy_item_flag=heavy
        ) if heavy else None,
        pickup_volume=f"{len(packages) or 1}",
        pickup_times=PickupTimesType(
            on_demand_pickup_time=OnDemandPickupTimeType(
                date=payload.date,
                preferred_time=payload.ready_time,
                closing_time=payload.closing_time
            ),
            scheduled_pickup_times=None
        ),
        payment_info=None
    )
    return Serializable(request, partial(_request_serializer, update=update))


def _request_serializer(request: PickupRequestDetails, update: bool = False) -> str:
    return export(
        request,
        name_=("pickup-request-update" if update else "pickup-request-details"),
        namespacedef_='xmlns="http://www.canadapost.ca/ws/pickuprequest"',
    )
