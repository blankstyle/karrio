import {
  AddressType,
  DEFAULT_ADDRESS_CONTENT,
  NotificationType,
  ShipmentType,
} from "@karrio/types";
import React, {
  FormEvent,
  useContext,
  useEffect,
  useReducer,
  useRef,
  useState,
} from "react";
import { COUNTRY_WITH_POSTAL_CODE, isEqual, isNone } from "@karrio/lib";
import { AddressAutocompleteInput } from "./address-autocomplete-input";
import { CheckBoxField } from "../components/checkbox-field";
import { useAPIMetadata } from "@karrio/hooks/api-metadata";
import { ButtonField } from "../components/button-field";
import { PostalInput } from "../components/postal-input";
import { InputField } from "../components/input-field";
import { PhoneInput } from "../components/phone-input";
import { NameInput } from "../components/name-input";
import { Notify } from "../components/notifier";
// import { CountryInput } from "./country-input";
import { Loading } from "../components/loader";
import { StateInput } from "./state-input";
import { CountrySelect } from "@karrio/ui/components/country-select";

interface AddressFormComponent {
  value?: AddressType;
  default_value?: AddressType | null;
  shipment?: ShipmentType;
  name?: "shipper" | "recipient" | "template";
  onSubmit: (address: AddressType) => Promise<any>;
  onTemplateChange?: (isUnchanged: boolean) => boolean;
  children?: React.ReactNode;
}

function reducer(
  state: any,
  { name, value }: { name: string; value: string | boolean | object },
) {
  switch (name) {
    case "full":
      return { ...(value as object) };
    case "partial":
      return { ...state, ...(value as object) };
    default:
      return { ...state, [name]: value };
  }
}

export const AddressForm = ({
  value,
  default_value,
  shipment,
  name,
  onSubmit,
  onTemplateChange,
  children,
}: AddressFormComponent): JSX.Element => {
  const { references } = useAPIMetadata();
  const { notify } = useContext(Notify);
  const form = useRef<HTMLFormElement>(null);
  const { loading, setLoading } = useContext(Loading);
  const [key, setKey] = useState<string>(`address-${Date.now()}`);
  const [address, dispatch] = useReducer(
    reducer,
    value || DEFAULT_ADDRESS_CONTENT,
  );
  const [advancedExpanded, setAdvancedExpanded] = useState<boolean>(false);

  const computeDisableState = (state: AddressType): boolean => {
    const isUnchanged = isEqual(value || DEFAULT_ADDRESS_CONTENT, state);

    return onTemplateChange ? onTemplateChange(isUnchanged) : isUnchanged;
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name: string = target.name;

    dispatch({ name, value });
  };
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      address.id && setLoading(true);
      await onSubmit(address);
      address.id &&
        notify({
          type: NotificationType.success,
          message: "Address successfully updated!",
        });
    } catch (err: any) {
      notify({ type: NotificationType.error, message: err });
    }
    setLoading(false);
  };

  useEffect(() => {
    if (
      value &&
      isNone(value.id) &&
      isNone(shipment?.id) &&
      !isNone(default_value)
    ) {
      dispatch({ name: "full", value: default_value as object });
      setKey(`address-${Date.now()}`);
    }
  }, [default_value, value]);
  useEffect(() => {
    if (
      shipment &&
      ["shipper", "recipient"].includes(name || "") &&
      !isEqual(shipment[name as "shipper" | "recipient"], address)
    ) {
      dispatch({
        name: "full",
        value: shipment[name as "shipper" | "recipient"],
      });
    }
  }, [shipment]);

  return (
    <form className="px-1 py-2" onSubmit={handleSubmit} key={key} ref={form}>
      {children}

      <div className="columns mb-0">
        <NameInput
          label="name"
          className="is-small"
          value={address.person_name}
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          disableSuggestion={isNone(shipment)}
          onValueChange={(value, refresh) => {
            dispatch({ name: "partial", value });
            refresh && setKey(`address-${Date.now()}`);
          }}
          required
        />
      </div>

      <div className="columns mb-0">
        <InputField
          label="company"
          name="company_name"
          onChange={handleChange}
          value={address.company_name}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          max={30}
        />
      </div>

      <div className="columns mb-0">
        <CountrySelect
          label="country"
          onValueChange={(value) =>
            dispatch({ name: "country_code", value: value as string })
          }
          value={address.country_code}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          required
        />
      </div>

      <div className="columns mb-0">
        <AddressAutocompleteInput
          label="Street (Line 1)"
          name="address_line1"
          onValueChange={(value) => dispatch({ name: "partial", value })}
          value={address.address_line1}
          country_code={address.country_code}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          required
        />
      </div>

      <div className="columns is-multiline mb-0">
        <InputField
          label="Unit (Line 2)"
          name="address_line2"
          onChange={handleChange}
          value={address.address_line2}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          max={50}
        />

        <InputField
          label="city"
          name="city"
          onChange={handleChange}
          value={address.city}
          className="is-small"
          wrapperClass="column is-6 px-1 py-3"
          fieldClass="mb-0 p-0"
          required
        />

        <StateInput
          label="province or state"
          onValueChange={(value) =>
            dispatch({ name: "state_code", value: value as string })
          }
          value={address.state_code}
          className="is-small"
          wrapperClass="column is-6 px-1 py-3"
          fieldClass="mb-0 p-0"
          country_code={address.country_code}
          required={Object.keys(references.states || {}).includes(
            address.country_code,
          )}
        />

        <PostalInput
          label="postal code"
          onValueChange={(value: string) =>
            dispatch({ name: "postal_code", value })
          }
          value={address.postal_code}
          country={address.country_code}
          className="is-small"
          wrapperClass="column is-6 px-1 py-3"
          fieldClass="mb-0 p-0"
          required={COUNTRY_WITH_POSTAL_CODE.includes(address.country_code)}
        />
      </div>

      <div className="columns mb-0">
        <InputField
          label="email"
          name="email"
          onChange={handleChange}
          value={address.email}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
          type="email"
        />

        <PhoneInput
          label="phone"
          onValueChange={(value: string) =>
            dispatch({ name: "phone_number", value })
          }
          value={address.phone_number}
          country={address.country_code}
          className="is-small"
          wrapperClass="column px-1 py-3"
          fieldClass="mb-0 p-0"
        />
      </div>

      <div className="columns mb-0 py-2">
        <CheckBoxField
          name="residential"
          onChange={handleChange}
          defaultChecked={address.residential}
          fieldClass="column mb-0 is-12 px-2 py-3"
        >
          <span>Residential address</span>
        </CheckBoxField>
      </div>

      {/* Advanced */}
      <div className="columns is-multiline mb-0 pt-4">
        <div
          className="column is-12 is-size-7 has-text-weight-bold has-text-info px-2 my-1 is-clickable"
          onClick={() => setAdvancedExpanded(!advancedExpanded)}
        >
          Advanced
          <span className="icon is-small">
            {advancedExpanded ? (
              <i className="fas fa-chevron-down"></i>
            ) : (
              <i className="fas fa-chevron-up"></i>
            )}
          </span>
        </div>

        <div
          className="columns column is-multiline mb-0 ml-6 my-1 px-2 py-0"
          style={{
            borderLeft: "solid 2px #ddd",
            display: `${advancedExpanded ? "block" : "none"}`,
          }}
        >
          <InputField
            label="federal tax id"
            name="federal_tax_id"
            onChange={handleChange}
            value={address.federal_tax_id}
            className="is-small"
            wrapperClass="px-2 py-2"
            fieldClass="column is-7 mb-0 p-0"
            max={20}
          />

          <InputField
            label="state tax id"
            name="state_tax_id"
            onChange={handleChange}
            value={address.state_tax_id}
            className="is-small"
            wrapperClass="px-2 py-2"
            fieldClass="column is-7 mb-0 p-0"
            max={20}
          />
        </div>
      </div>

      <div className="p-3 my-5"></div>
      <ButtonField
        type="submit"
        className={`is-primary ${loading ? "is-loading" : ""} m-0`}
        fieldClass="form-floating-footer p-3"
        controlClass="has-text-centered"
        disabled={computeDisableState(address)}
      >
        <span>
          {isNone(shipment?.id) && name !== "template" ? "Next" : "Save"}
        </span>
      </ButtonField>
    </form>
  );
};
