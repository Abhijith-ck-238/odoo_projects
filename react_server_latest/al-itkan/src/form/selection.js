import React, {useContext, useEffect, useState} from 'react'
import { Context } from "../store"

export default function Radio ({name, ops, classes, values, placeholder}) {
  const [state,setState] = useContext(Context)
  const [val, setVal] = useState("");

  useEffect(() => {
    if (state['data'][name] === undefined){
      state['data'][name] = !!values ? values[0] : ops[0].toLowerCase()
      
      console.log(state)
      setState(state)    
    } 
      setVal(state['data'][name])    
  }, [])

  let handleChange = (e) => {
    let value = !!values ? Number(e.target.value) : e.target.value
    state['data'][name] = value
    setVal(value);
   
    console.log(state)
    setState(state)
  }
const _onFocus=(e)=>{
  e.target.type = "date";
}
  return (
    <select onChange={handleChange} value={val}
    className={"border-b-2 border-black-400 focus:border-blue-500 outline-none  bg-none " + (!!classes ? classes: "")} placeholder={placeholder}>
      {ops.map((op, index) => {
        let formated_op = op.toLowerCase().split(' ').join('_')
        return (
          <option value={!!values ? values[index] : formated_op}
          className="text-gray-600 " key={index}>
            {op}
          </option>
        )}
      )}

    </select>
  )
}

