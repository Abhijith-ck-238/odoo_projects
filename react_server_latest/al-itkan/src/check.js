import React, { useState, useContext } from "react";
import { Button } from "./App";
import { Context } from "./store";
import Back from './asstes/icon-arrow-back.svg'
import { Link } from 'react-router-dom'
const axios = require("axios");

export default function Check() {
  const [state] = useContext(Context);
  const [check, setCheck] = useState("");

  let handleCheck = (e) => {
    axios.post(`${process.env.REACT_APP_BASE_URL}/api/check`, state).then((res) => {
      console.log("responseee ", res, res.data.msg);
      let msg = res.data.msg
      setCheck(msg)
    }).catch(err => {
      // what now?
      console.log(err);
    })
  };

  let handleChange = (e) => {
    let value = e.target.value;
    state["ref"] = value;
    console.log(state)
  };

  return (
    <>
      <h3 className="text-center mt-10 lg:text-2xl md:text-2xl sm:text-sm">
        Check your application status
      </h3>

      <div className="flex flex-col lg:w-3/4 md:w-3/4 rounded bg-white shadow-lg mx-auto mt-16  px-10 py-4 sm:w-3/4 ">
        <Link to="/">
          <img src={Back} className="w-4 h-4 mt-4 object-cover" alt="back button" />
        </Link>
        <input
          placeholder="Enter your reference number"
          name="check"
          onChange={handleChange}
          className="pt-8 border-b-2 border-black-400 focus:border-blue-500  outline-none lg:px-4 md:px-4 sm:px-0  "
        />
        <div className="px-4 my-4">
          <Button onClick={handleCheck} value="Check status" />
        </div>

        {/* the string that should be displayed here is returned from the post request */}

        {check ? <span className="text-red-400 my-8">{check}</span> : null}
      </div>
    </>
  );
}
