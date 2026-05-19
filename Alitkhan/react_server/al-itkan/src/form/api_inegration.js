import React,{useEffect, useState, useContext} from 'react'
import { useForm} from "react-hook-form";
import { FormInput, Button } from "../App";
import {Context} from '../store'
const axios = require("axios");

export default function Api_inegration() {
//  const [state, setState] = useContext(Context)

//   let handleSubmit = (e) => {
//     axios.post("https://jobsbackend.alitkan.com/api", {
//       headers: {"Content-Type": "application/json"}
//     }).then((response) => {
//       console.log("response =", response);
//     })

    // fetch("http://191.101.164.149:5000/api", {
    //   method: "POST",
    //   body: JSON.stringify(state),
    //   headers: {
    //     "Content-Type": "application/json",
    //   },

    // }).then((response) => {
    //   //  res = onSubmit
    //   console.log("response =", response);
    // })
  }    



  return (
    <div>
      <Button value="submit" onClick={handleSubmit}/>
    </div>
  )
}
