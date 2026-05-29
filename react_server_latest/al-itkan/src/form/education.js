import React, { useState, useContext, useEffect } from "react";
import { FormInput, Button, R_link, check_job_id } from "../App";
import { Link } from "react-router-dom";
import { Operations } from "./family info";
import Radio from './radio'
import Selector from './selection'
import {Context} from '../store'
import { Training } from "./skills";

export default function Education() {
  const [state, setState] = useContext(Context)
  const [show, setShow] = useState([]);
  const [hidePrev, setHidePrev] = useState(true);
  const [hideNext, setHideNext] = useState(false);

  const required_fields = ['secondary_name', 'secondary_years', 'secondary_avg',
    'college_name', 'college_years', 'college_avg',
    'highest_acad', 'highest_grad_year', 'highest_uni', 'highest_country',
    't0', 't0_year', 't0_awarded_by', 't0_country_city','college_major']

  useEffect(() => {
    check_job_id(state, setState)
  }, [])

  return (
    <div className=" lg:w-3/4 md:w-3/4  rounded overflow-hidden bg-white shadow-lg mx-auto mt-10 p-8  sm:w-full">
      <h3 id="page_title" className="my-8 text-2xl "> Education </h3>
      <div className="border border-gray-300 rounded p-6">
      <div className="lg:flex md:flex  sm:block  flex-row justify-between mx-auto  ">

        <div className="flex flex-col lg:mx-8 md:mx-8 sm:mx-2 mb-4 lg:w-1/2 md:w-1/2 sm:w-full">
          <p className="text-start my-4">Secondary </p>
          <FormInput placeholder="Name of school" name="secondary_name"/>
          <FormInput placeholder="Years" name="secondary_years"/>
          <FormInput placeholder="Average %" name="secondary_avg" type="number"/>
        </div>

        <div className="flex flex-col  lg:mx-8 md:mx-8 sm:mx-2 mb-4 lg:w-1/2 md:w-1/2 sm:w-full ">

          <p className="text-start my-4">College or institute</p>
              <FormInput placeholder="Name of school" name="college_name" />
              <FormInput placeholder="Major" name="college_major" />
              <FormInput placeholder="Years" name="college_years"/>
              <FormInput placeholder="Average %" name="college_avg" type="number"/>


        {show.map((input, index) => {
          let n = index;
          return (
            <div className="flex flex-col  lg:mx-8 md:mx-8 sm:mx-2 mb-4 mt-8 " key={index}>
              <FormInput placeholder="Name of school" name={"other_"+ n +"_name"} />
              <FormInput placeholder="Major" name={"other_"+ n +"_major"} />
              <FormInput placeholder="Years" name={"other_"+ n +"_years"}/>
              <FormInput placeholder="Average %" name={"other_"+ n +"_avg"} type="number"/>
            </div>
          );
        })}
        </div>
      </div>


        <div className="flex  justify-around flex-row mt-8 ">
        {/* <p className="text-red-400">Add more education</p> */}

          {hideNext ? null : (
          <Operations
            onClick={() => {
              setShow([...show, {}]);
              setHideNext(show.length == 1 ? true: false)
              setHidePrev(false);
            }}
            operation="Add more education"
          /> )}

          {hidePrev ? null : (
            <Operations
              onClick={() => {
                setShow(show.slice(0, show.length - 1));
                // I put 2 bcause ths show value is before the intitaliting fo setShow()
                setHidePrev(show.length == 1 ? true : false)
                setHideNext(false)
                let last_index = show.length - 1
                delete state['data']["other_"+ last_index +"_name"]
                delete state['data']["other_"+ last_index +"_major"]
                delete state['data']["other_"+ last_index +"_years"]
                delete state['data']["other_"+ last_index +"_avg"]
                setState(state)
              }}
              operation="Remove"
            />
          )}
      
      </div>


      <div className="flex flex-col my-12  lg:px-20 md:px-20 sm:px-2">
          <FormInput
            placeholder="Highest academic qualification "
            name="highest_acad"
          />
          <FormInput placeholder="Academic major" name="major"/>
          <FormInput placeholder="Graduation year " name="highest_grad_year"/>
          <FormInput placeholder="University" name="highest_uni" />
          <FormInput placeholder="Country" name="highest_country" />
        </div>
</div>
        <Training/>

      <div className="flex justify-around flex-row mt-8">
        <Link to="/personal">
          <Button value="Previous" />
        </Link>
        <R_link fields={required_fields} route="/technical" value="Next"/>
      </div>
    </div>
  );
}
