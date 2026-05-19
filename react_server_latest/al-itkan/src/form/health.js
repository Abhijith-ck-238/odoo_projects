import React from "react";
import {Button} from '../App';
import {Link } from 'react-router-dom'
import Radio from './radio'


export default function Health() {
 

  return (
      <div className=" my-12 lg:p-8 md:p-8 sm:p-4">
      <h3 className="my-8 text-2xl " > Health and Limitation </h3>
        <div className="flex  flex-col mb-4 border border-gray-300 rounded p-6">
        <div className="my-4  lg:flex  md:flex sm:block jusitfy-left  ">
          <label className="p-4 " htmlFor="helath_status"> Your health status ? </label>
        <div className="flex flex-row  w-full my-4">
          <Radio name="health_status" ops={['Excellent', 'Good', 'Average',
          'Below average', 'Poor', 'Very poor']} />
          </div>
        </div>

        {/* <div className="my-4 lg:flex  md:flex sm:block jusitfy-left ">
          <label className="p-4 " htmlFor="disease">Have you suffered or are you suffering from any terminal illness or chronic disease? </label>
          <div className="flex flex-row  justify-center my-4" >
            <Radio name="disease" ops={['Yes', 'No']} />
          </div>
        </div> */}
  
        <div className="my-4  lg:flex  md:flex sm:block jusitfy-left  ">
          <label className="p-4 " htmlFor="limitation">Are there any limitations on your ability to perform in your prospective field of work? </label>
          <div className="flex flex-row  justify-center my-4" >
            <Radio name="limitaions" ops={['Yes', 'No']} />
          </div>
        </div>

        <div className="my-4  lg:flex  md:flex sm:block jusitfy-left  ">
          <label className="p-4 " htmlFor="travel_limitation"> Are there any limitations on your ability to engage in all types of travel? Inside or outside Iraq </label>
          <div className="flex flex-row  justify-center my-4">
            <Radio name="limitaions_travel" ops={['Yes', 'No']} />
          </div>
        </div>

    </div>  
      <div className="mb-4"/>

    </div>
  );
}
