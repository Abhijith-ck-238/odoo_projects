import React, { useState, useContext, useEffect } from "react";
import { Context } from "../store";
import Down from "../asstes/arrow-down.svg";
import {Link} from 'react-router-dom';
import { css } from "@emotion/core";
import PreLoader from '../asstes/preloader.svg';
import ClipLoader from "react-spinners/ClipLoader";
import './job.css';

const axios = require("axios");
const override = css`
  display: block;
  border-color: #ed8936;
`; 




export default function Description() {
  const [desc,setDesc] = useState({})
  const [loading, setLoading] = useState(true);

    useEffect(()=>{
      async function fetchData() {
      let url = new URL(document.URL);
      let job_id = Number( url.searchParams.get("job_id"))
       await axios.get(`http://173.249.59.179:5000/api/description?job_id=${job_id}`)
       .then(res =>  {
          let data = {...res.data};
          data['type_of_position'] = data.type_of_position
          Object.assign(desc, data.job)
          setDesc({...desc})
          console.log("state =",desc)
          if (res) setLoading(false);

     })
       }
  fetchData()
  console.log("desc out side ", desc)
    },[])


    const style= (
      desc.state=="open" ? {backgroundColor:'#e2e8f0',minHeight:'100vh'  }: {backgroundColor:'white',minHeight:'100vh'  }
    )
  return (
    <div>
       {loading ? (
        <div className="mt-64 mx-auto">
         <img src={PreLoader} width="100" height="100" className="mx-auto" />
          <p className="text-center">
            Jobs still loading ...{" "}
          </p>
        </div>
        // </div>
        )
        :desc.state!='open' ? 
               <div className="py-10 ">
                <h2 className="text-left text-2xl lg:ml-16 md:ml-12 sm:ml-0 mt-24">{desc.name}</h2>

                <Basic_info department={desc.department_id ? desc.department_id[1] : "On Intreview"}
                  emp_type={desc.type_of_position ? 
                    desc.type_of_position == "full_time" ? 
                      "Full Time"
                      :
                      "Part Time" 
                    :
                    "On Intreview"}
                  location={desc.city ? desc.city : "On Intreview"} />

                <div className="rounded overflow-hidden bg-white shadow-lg mx-10">
                { desc.description ?
                  <Drop_down
                  title="Summary"
                  content={desc.description}
                  />
                : null}
                
                { desc.behavioral_competencies ?
                  <Drop_down
                  title="Behavioral Competencies"
                  content={desc.behavioral_competencies}
                  />
                : null}

                { desc.technical_knowledge ?
                  <Drop_down
                  title="Technical Knowledge"
                  content={desc.technical_knowledge}
                  />
                : null}

                { desc.education_language_requirements ?
                  <Drop_down
                  title="Education and Language Requirements"
                  content={desc.education_language_requirements}
                  />
                : null}

                <Link to={`/personal?job_id=${desc.id}`}>
                      <button
                        className="px-4 py-2 mt-8  mb-8  border border-orange-600 bg-transparent text-orange-600 hover:bg-orange-700 active:bg-orange-700  rounded hover:text-white active:text-white mb-2  transition ease-linear duration-500"
                      >
                        Apply 
                      </button>
                    </Link>
                </div>
            </div> 
       :desc.state=="open" ?  <div className="py-10 "> 
             <h2 className=" text-left text-2xl lg:ml-12 md:ml-10 sm:ml-4 mt-24">{desc.name} </h2>
                <Basic_info department={desc.department_id ? desc.department_id[1] : "on intreview"}
                  emp_type={desc.type_of_position ? desc.type_of_position : "on intreview"}
                  location={desc.city} />

                <div className="rounded overflow-hidden bg-white shadow-lg mx-10">
                { desc.description ?
                  <Drop_down
                  title="Summary"
                  content={desc.description}
                  />
                : null}
                
                { desc.behavioral_competencies ?
                  <Drop_down
                  title="Behavioral Competencies"
                  content={desc.behavioral_competencies}
                  />
                : null}

                { desc.technical_knowledge ?
                  <Drop_down
                  title="Technical Knowledge"
                  content={desc.technical_knowledge}
                  />
                : null}

                { desc.education_language_requirements ?
                  <Drop_down
                  title="Education and Language Requirements"
                  content={desc.education_language_requirements}
                  />
                : null}
                <h3 className="text-center text-xl mt-10"> This job is not available right now </h3>
                <Link to="/">
                      <button
                        className="px-4 py-2 mt-8  mb-8 border border-blue-400 bg-transparent text-blue-400 hover:bg-blue-500 active:bg-blue-500  rounded hover:text-white active:text-white mb-2  transition ease-linear duration-500"
                      >
                        Back 
                      </button>
                    </Link>
                </div>
    
                </div>

                :null}
    </div>
  );
}

const Drop_down = ({ title, content }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="mb-4">
      <h4
        className="flex justify-between hover:border-transparent text-orange-500  text-left py-4 pl-4  lg:text-xl md:text-xl sm:text-sm hover:bg-orange-500  focus:bg-orange-500 hover:bg-orange-500  focus:text-white hover:text-white "
        onClick={() => setShow(!show)}
      >
        {" "}
        {title}
      </h4>
      {show ? (
        <div className="bg-gray-200 w-full p-8">
          {content.split('\n').map((line) => {
            return (<p className="text-left">{line}</p>)
          })}
        </div>
      ) : null}      
    </div>
  );
};

const Basic_info = ({ department, emp_type, location }) => {
  return (
    <div className="flex flex-row  lg:mx-12 md:mx-12 sm:mx-4 justify-between my-8">
      <div className="flex flex-col lg:mx-12  md:mx-12 flex-wrap sm:mx-4 xs:mx-4 justify-between">
        <p className="text-orange-600 text-sm" > Department </p>
        <p className="text-black lg:text-lg md:text-lg sm:text-sm"> {department}</p>
      </div>
      <div className="flex flex-col justify-between ">
        <p className="text-orange-600 text-sm mx-4" >
          {" "}
          Employment Type{" "}
        </p>
        <p className="text-black lg:text-lg md:text-lg sm:text-sm"> {emp_type}</p>
      </div>
      <div className="flex flex-col justify-between ">
        <p className="text-orange-600  text-sm mx-4" > Location </p>
        <p className="text-black lg:text-lg md:text-lg sm:text-sm">{location}</p>
      </div>
    </div>
  );
};

