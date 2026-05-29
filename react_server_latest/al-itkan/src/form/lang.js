import React,{useState, useContext} from "react";
import { Button,FormInput } from "../App";
import { Link } from "react-router-dom";
import Selector from './selection'
import {Context} from '../store'

export default function Language() {

  const [state, setState] = useContext(Context)
  const [show , setShow] =useState([])
  const [hidePrev, setHidePrev] = useState(true);
  const [hideNext, setHideNext] = useState(false);

  return (
    <div>
      <div className="mx-auto my-10 lg:p-8 md:p-8 sm:p-4 ">
          <h2 className="mt-8 text-2xl"> Language and Level of Proficiency </h2>
<div className="border border-gray-300 rounded p-6">
           <div className="mt-4 lg:flex md:flex  flex-row justify-center sm:block">

            <LangaugeSection name="Arabic" logic_name="ar"/> 

            <LangaugeSection name="English" logic_name="en"/> 
      
           </div>
           <div className="flex flex-col mx-4">
           {show.map((input, index) => {
            let n = index;
            return (
              <div className="flex flex-col mt-8 px-8 justify-center" key={index}> 
              <FormInput placeholder={"Add the name of language you know"}
              className="my-8" name={"other_name_"+n}/>

              <label htmlFor="arabic" className="mt-4">Reading</label>
              <Selector name={"other_r_" + index} classes="text-sm text-gray-600"
              ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
              "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

              <label htmlFor="arabic" className="mt-4"> Writing</label>
              <Selector name={"other_w_" + index} classes="text-sm text-gray-600"
              ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
              "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

              <label htmlFor="arabic" className="mt-4"> Speaking</label>
              <Selector name={"other_s_" + index} classes="text-sm text-gray-600"
              ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
              "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

              <label htmlFor="arabic" className="mt-4"> Understanding</label>
              <Selector name={"other_u_" + index} classes="text-sm text-gray-600"
              ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
              "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

              <label htmlFor="arabic" className="mt-4" > Overall </label>
              <Selector name={"other_o_" + index} classes="text-sm text-gray-600"
              ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
              "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>


           </div> 
           )})}
        </div>
     
          <div className="lg:flex md:flex justify-around flex-row mt-8  sm:block">
           {/* <p className="text-red-400">Add more language ( just two allowed ) </p>  */}
           {hideNext ? null : <button
              className="px-6 bg-gray-500 hover:bg-gray-600 focus:bg-gray-600 rounded text-white  focus:text-white"
              onClick={() => {
                setShow([...show, {}])
                setHideNext(show.length == 1 ? true: false)
                setHidePrev(false);
                }}
           >
              Add more
            </button> }

            { hidePrev ? null : <button onClick={(index) => {
                setShow(show.slice(0, show.length - 1))
                setHidePrev(show.length == 1 ? true : false)
                setHideNext(false)
                let last_index = show.length - 1
                delete state['data']['other_name_' + last_index]
                delete state['data']['other_r_' + last_index]
                delete state['data']['other_w_' + last_index]
                delete state['data']['other_s_' + last_index]
                delete state['data']['other_u_' + last_index]
                delete state['data']['other_o_' + last_index]
                setState(state)
            }} className="px-6 bg-gray-500 hover:bg-gray-600 focus:bg-gray-600 rounded text-white  focus:text-white">
              Remove
            </button>}  
          </div>
      </div>
        </div>
        <div className="mb-4"/>
    </div>
  );
}

const LangaugeSection = ({name, logic_name}) => {
  return <div className="flex flex-col mx-4 lg:w-1/2 md:w-1/2 sm:w-full ">
      <p className="mb-8 mt-4 text-xl"> {name}</p>

      <label htmlFor="arabic" className="mt-4">Reading</label>
      <Selector name={logic_name + "_r"} classes="text-sm text-gray-600"
      ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
      "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

      <label htmlFor="arabic" className="mt-4"> Writing</label>
      <Selector name={logic_name + "_w"} classes="text-sm text-gray-600"
      ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
      "poor", 'Very poor']} values={[7,6,5,4,3,2,1]} />

      <label htmlFor="arabic" className="mt-4"> Speaking</label>
      {/* <option value ="" selected>speak</option> */}
      <Selector name={logic_name + "_s"} classes="text-sm text-gray-600"
      ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
      "poor", 'Very poor']} values={[7,6,5,4,3,2,1]} />

      <label htmlFor="arabic" className="mt-4"> Understanding</label>
      <Selector name={logic_name + "_u"} classes="text-sm text-gray-600"
      ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
      "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

      <label htmlFor="arabic" className="mt-4" > Overall </label>
      <Selector name={logic_name + "_o"} classes="text-sm text-gray-600"
      ops={['Excellent', 'Very good', 'Good', 'Average', "Below average",
      "poor", 'Very poor']} values={[7,6,5,4,3,2,1]}/>

    </div>

}

export const SelectField = ({language,forValue})=>{
  return <div className="flex flex-col mx-4 w-1/2">
  <p className="mb-8  mt-4 text-xl"  htmlFor={forValue}> {language}</p>

  <label htmlFor="arabic" className="mt-4">Read</label>
  <Selector name="ar_r" classes="text-sm text-gray-600"
  ops={['Excellent', 'Very good', 'Good', 'Average', "Below average"]} />

  <label htmlFor="arabic" className="mt-4"> Write</label>
  <Selector name="ar_w" classes="text-sm text-gray-600"
  ops={['Excellent', 'Very good', 'Good', 'Average', "Below average"]} />

  <label htmlFor="arabic" className="mt-4"> Speak</label>
  <Selector name="ar_s" classes="text-sm text-gray-600"
  ops={['Excellent', 'Very good', 'Good', 'Average', "Below average"]} />

  <label htmlFor="arabic" className="mt-4"> Understand</label>
  <Selector name="ar_u" classes="text-sm text-gray-600"
  ops={['Excellent', 'Very good', 'Good', 'Average', "Below average"]} />

  <label htmlFor="arabic" className="mt-4" > Overall </label>
  <Selector name="ar_o" classes="text-sm text-gray-600"
  ops={['Excellent', 'Very good', 'Good', 'Average', "Below average"]} />
  </div>
}
