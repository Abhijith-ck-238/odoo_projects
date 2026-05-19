import React, {useContext, useState, useEffect} from 'react'
import { Context } from "../store"

export default function Radio ({name, ops, mx}) {
  const [state,setState] = useContext(Context)
  const [val, setVal] = useState("");

  
  useEffect(() => {
      if(state['data'][name])
       setVal(state['data'][name])
  }, []);



  let handleChange = (e) => {
   let value = e.target.value
    state['data'][name] = value
    setVal(value);
    console.log(state)
    setState(state)
  }

  return (
    <div className={"flex flex-row  flex-wrap " + (mx ? "mx-auto" : "")}>
      {ops.map((op, index) => {
        let formated_op = op.toLowerCase()
        return (
        <div className="ml-2 flex flex-row" key={index}>
          <label className="text-gray-600"> {op} </label>{" "}
          <input
            type="radio"
            className="checked:bg-gray-900 checked:border-transparent ml-2 mt-2 text-gray-300 "
            onChange = {handleChange}
            checked={val===formated_op}
            value={formated_op}
            name={name}
            />
        </div>
        )
      })
    }

    </div>
  )
}
