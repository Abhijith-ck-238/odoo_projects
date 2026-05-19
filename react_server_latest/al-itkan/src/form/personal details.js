import { FormInput, R_link, check_job_id} from "../App";
import { Link } from "react-router-dom";
import Family from "./family info";
import Health from "./health";
import Language from "./lang";
import React, { useEffect, useContext } from "react";
import Radio from "./radio";
import Selector from "./selection";
import { Context } from "../store";
import LOGO from '../asstes/PIONEERS.png'

export default function PersonalDetails() {
  const [state, setState] = useContext(Context);
 
  useEffect(() => {
    check_job_id(state, setState,true, true)
    state["data"]["filling_time"] = new Date();
    setState(state);
    console.log("start ", state["data"]);
  }, []);

  const _onFocus = (e) => {
    e.target.type = "date";
  };

  return (
    <div className="lg:w-3/4 md:w-3/4 rounded overflow-hidden bg-white shadow-lg mx-auto mt-10 p-8 sm:w-full">
   <div className="mt-16">
      <img src={LOGO} className="w-48 h-12 object-content mx-auto mb-4"/>
      <h3 id="page_title" className="mt-0 mb-10 text-2xl "> Personal Details </h3>
      </div>
      <div className="lg:flex md:flex sm:block lg:flex-row md:flex-row sm:flex-col justify-between mx-auto ">
        <div className="flex flex-col  mx-8 mb-4 lg:w-1/2 md:w-1/2 sm:w-full border border-gray-300 rounded p-6">
          <FormInput placeholder="Full name (الاسم الرباعي باللغة الانكليزية)" name="name" type="text"/>

          {state['check_length'] ? <p className="text-xs text-red-500">please, write your full name (include your first, mid and last name)</p> : null }


          <FormInput placeholder="Sur name (اللقب)" name="surname" type="text" />
          <FormInput placeholder="الاسم الرباعي باللغة العربية" name="arabic_name" type="text" />
          <FormInput placeholder="Email" name="email_from" type="email" />
          <FormInput
            placeholder="Phone number"
            name="partner_phone"
            type="text"
          />
          <FormInput placeholder="Address" name="address" type="text" />
          <FormInput placeholder="Hai/region" name="hai" type="text" />
          <FormInput placeholder="Section" name="sec" type="text" />
          <FormInput placeholder="Street" name="st" type="text" />
          <FormInput placeholder="House" name="house" type="text" />
          <FormInput
            textarea={true}
            placeholder="Nearest point of reference"
            name="nearest"
            type="text"
            className="pb-4 border-b-2 border-black-400 focus:border-blue-500  outline-none p-2"
          />
        </div>
        <div className="flex flex-col mx-8 mb-4 lg:w-1/2 md:w-1/2 sm:max-w-xl border border-gray-300 rounded p-6">
          <FormInput placeholder="Birth date" type="text" name="birthdate" onFocus={_onFocus}/>
          <FormInput
            placeholder="Place of birth"
            name="place_of_birth"
            type="text"
          />
          {/* <input onblur={checkLength} id="groupidtext" type="text"  maxlength="6" placeholder="trying"/> */}
          <label className="p-4">Gender</label>
          <Radio name="gender" ops={["Male", "Female"]} mx="mx-auto" />
          <FormInput placeholder="Height" name="height" type="number" />
          <FormInput placeholder="Weight" name="weight" type="number" />
          <FormInput placeholder="Citizenship" name="citizenship" type="text" />
          <FormInput placeholder="Religion" name="religion" type="text" />

          <label className="p-4">Social Status</label>
          <Selector
            name="social_status"
            classes="p-2"
            ops={[
              "Single",
              "Engaged",
              "Married",
              "Seperated",
              "Widowed",
              "Divorced",
            ]}
          />
        </div>
        <div className="mb-4" />
      </div>

      {/*  added more info to the basic page  */}
      <Family />
      <div className="my-10" />
      <div className=" my-12 lg:p-8 md:p-8 sm:p-4">
        <div className="flex  flex-col mb-4 border border-gray-300 rounded p-6">
          <p className="mt-4 ml-12"><b> Emergency contact person (Family member preferable): </b></p>
          <div className="flex flex-row my-10 justify-around flex-wrap">
              <p className="mt-4 ml-12"> Full Name: </p>
              <FormInput placeholder="name" name="emergency_contact_name" />
              <p className="mt-4 ml-12"> Phone No.: </p>
              <FormInput placeholder="phone no" name="emergency_contact_phone" />
              <p className="mt-4 ml-12"> Relation: </p>
              <FormInput placeholder="relation" name="emergency_contact_relation" />
          </div>
          <div className="flex flex-row my-10 justify-around flex-wrap">
              <p className="mt-4 ml-12"> <b>If You have been Interviewed Earlier by ALITKAN, Please Provide the date:</b> </p>
              <FormInput placeholder="date" type="text" name="past_interview_date" onFocus={_onFocus} />
          </div>
        </div>
      </div>
      <div className="my-10" />
      <Health />
      <div className="my-10" />
      <Language />

      <div className="mt-10">
        <R_link
          fields={[
            "name",
            "surname",
            "email_from",
            "partner_phone",
            "address",
            "hai",
            "sec",
            "st",
            "house",
            "nearest",
            "birthdate",
            "place_of_birth",
            "gender",
            "height",
            "weight",
            "citizenship",
            "religion",
            "father_profession",
            "mother_profession",
            "health_status" ,
            // "disease",
            "limitaions",
            "limitaions_travel",
            "arabic_name",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relation",
            // "past_interview_date",
          ]}
          route="/education"
          value="Next"
        />
      </div>
      <div className="mb-4" />
    </div>
  );
}
