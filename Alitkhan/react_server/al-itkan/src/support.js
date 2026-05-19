import React, { useEffect, useContext, useState } from "react";
import { FormInput, Button, R_link } from "./App";
import { Context } from "./store";
import { Link, Redirect } from "react-router-dom";
import { SelectField } from "./form/lang";
import Selector from './form/selection';
const axios = require("axios");

export default function Support() {
  const [state, setState] = useContext(Context);

  return (
    <div className="lg:w-3/4 md:w-3/4  rounded overflow-hidden bg-white shadow-lg mx-auto mt-24 p-8 sm:w-full" style={{minHeight:'100vh'}} >
      <h3 className="mb-8 mt-4 text-2xl "> Support </h3>
      <div className="lg:flex md:flex sm:block lg:flex-row md:flex-row sm:flex-col justify-between mx-auto ">
        <div className="flex flex-col  mx-8 mb-4 lg:w-full md:w-full sm:w-3/4 ">
          <FormInput name="partner_name" type="text" placeholder="Your Name*" />
          <FormInput
            name="partner_email"
            type="text"
            placeholder="Your Email*"
          />
          <FormInput name="phone_number" type="text" placeholder="Your Phone Number*" />
          <FormInput name="name" type="text" placeholder="Subject*" />
          <FormInput name="hospital_name" type="text" placeholder="Hopital Name" />
          <Selector  placeholder="Provinces*" 
                name="province"
                ops={[
                "Baghdad",
                "Diyala",
                "Basra",
                "Dohuk",
                "Karbla",
                "Najaf",
                "Al-Qadisiyyah",
                "Al Anbar",
                "Babil",
                "Dhi Qar",
                "Sulaymaniyah",
                "Kirkuk",
                "Erbil",
                "Saladin",
                "Halabja",
                "Maysan",
                "Muthanna",
                "Nineveh",
                "Wasit"
                ]}
                classes="my-4" />
          <FormInput name="unit_type" type="text" placeholder="Unit type" />
          <FormInput name="unit_serial_number" type="text" placeholder="Unit Serial Number" />
          <FormInput name="uploaded_file" type="file" placeholder="Upload File"/>
          <FormInput name="brand_name" placeholder="Brand Name"/>
          <FormInput name="user_description" type="text" placeholder="Description*" />
          <div className="px-4 my-4">
            <p id="loading_text" className="hidden mb-4"> please wait...</p>

            <R_link value="Submit" fields={["name", "partner_name","partner_email","phone_number","user_description","province"]} route="/ticket_submitted"
            // url="http://erp.alitkan.com:5000/api/helpdesk" stateKey="help_desk_ticket"/>
            url="https://jobsbackend.alitkan.com/api/helpdesk" stateKey="help_desk_ticket"/>

          </div>
        </div>
      </div>
    </div>
  );
}

export const Ticket_submitted = () => {
  const [state, setState] = useContext(Context);

  return (
    <div className="max-w-xl rounded overflow-hidden bg-white shadow-lg mx-auto mt-24 p-8" >
      
      { state.help_desk_ticket ?
          state.help_desk_ticket.created ? 
          <p className="text-center text-2xl mb-8">
            Your ticket has been submitted successfully,
            <br/>
            <span className="">Our support staff will
            contact you shorty</span>
          </p> 
          : 
          <p> Something went wrong when submiting you ticket. Please try again later </p>

        :

        <p className="text-center text-lg mb-8">
          No Ticket is submited. Please go back to the ticket page 
        </p> 

      }
    
    </div>
  );
};

