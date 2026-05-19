import React, { useContext, useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { Link } from "react-router-dom";
import Store, { Context } from "./store";
import PersonalDetails from "./form/personal details";
import Education from "./form/education";
import Admin_Skills, {
  Sales_Skills,
  Training,
  Technical_skills,
} from "./form/skills";
import Employment_history, {
  Refrence,
  Submited,
  Additional_info,
} from "./form/employment";
import Support, { Ticket_submitted } from "./support";
import Check from "./check";
import Jobs from "./jobs/jobs";
import Header from "./header";
import { Footer } from "./header";
import Description from "./jobs/description";
const axios = require("axios");

export let check;

function App() {
  return (
    <>
      <Header />
      <div className="App">
        {/* Itkan main nav bar goes here  */}
        <Store>
          <Router>
            <Switch>
              <Route exact path="/" component={Jobs} />
              <Route path="/jobs/description" component={Description} />
              {/* <Route  path="/closedjobs/description" component={Closed_desc}/>  */}
              <Route path="/personal" component={PersonalDetails} />
              <Route path="/education" component={Education} />
              <Route path="/check" component={Check} />
              <Route path="/technical" component={Technical_skills} />
              <Route path="/admin_skills" component={Admin_Skills} />
              <Route path="/sales_skills" component={Sales_Skills} />
              <Route path="/training" component={Training} />
              <Route path="/employment" component={Employment_history} />
              <Route path="/additional" component={Additional_info} />
              <Route path="/refrence" component={Refrence} />
              <Route path="/submited" component={Submited} />
              <Route path="/helpdesk" component={Support} />
              <Route path="/ticket_submitted" component={Ticket_submitted} />
              {/* <Route path="/page_details" component={Page_details}/> */}
            </Switch>
          </Router>
        </Store>
      </div>
      <Footer />
    </>
  );
}

export default App;
export const msg =()=>{
  return <p>please </p>
}
export const FormInput = ({
  placeholder,
  name,
  type,
  textarea,
  onFocus,
  maxLength,
  pattern,
  title,
  id
}) => {
  const [state, setState] = useContext(Context);
  const [val, setVal] = useState("");
  const [checkLen, setcheck] = useState(false);
  useEffect(() => {
    if (state["data"][name]) setVal(state["data"][name]);
  }, []);

  const handleChange = (e) => {
    check = false;
    let type = e.target.type;
    if (type === "file") {
      let file = e.target.files[0];
      if (file) {
        if (file.size > 10e6) {
          alert("file is too big, please upload file less than 10MB");
          e.target.value = null;
        } else {
          let reader = new FileReader();
          reader.onloadend = function () {
            let b64 = reader.result.replace(/^data:.+;base64,/, "");
            state["files"][name] = b64;
            state["files"]["original_" + name] = file;
            //  e.target.classList.remove("missing")
          };
          reader.readAsDataURL(file);
        }
      }
    } else {
      let value = e.target.value;
      state["data"][name] = type == "number" ? Number(value) : value;
      e.target.classList.remove("missing");
      setVal(value);

      
      // }
    }
    // if (e.target.value.length < "11") {
      // state["check_length"] = true;
      // setState(state)
      // alert("please full your name adel")
      // setState(() => (state["check_length"] = true));
      // setVal(e.target.value)
    // }


    setState(state);
  };

  if (!!textarea) {
    return (
      <textarea
        type={type}
        placeholder={placeholder}
        name={name}
        onChange={handleChange}
        className="pb-4 border-b-2 border-black-400 focus:border-blue-500  outline-none p-2"
        value={val}
        pattern={pattern}
        title={title}
        id={id}
      />
    );
  } else {
    return (
      <input
        type={type}
        placeholder={placeholder}
        name={name}
        onChange={handleChange}
        onFocus={onFocus}
        className="border-b-2 border-black-400 focus:border-blue-500 outline-none p-2"
        value={type == "file" ? undefined : val}
        maxLength={maxLength}
        pattern={pattern}
        title={title}
        id={id}
      />
    );
  }
};

export const R_link = ({ route, fields, value, url, stateKey, onClick }) => {
  const [state, setState] = useContext(Context);
  let full_path = `${route}?job_id=${state.data.job_id}`
  console.log(full_path)
  let handle_click = async (e) => {
    let missingField = [];
    for (let x in fields) {
      let item = fields[x];
      if (!state["data"][item] && !state["files"][item]) {
        var element = document.getElementsByName(item)[0];
        if (element.placeholder) missingField.push(element.placeholder);
        else missingField.push(item);
        element.classList.add("missing");
      }
    }
    let link = document.getElementsByName("rLink")[0];

    let name_field = document.getElementsByName("name")[0];
    if (name_field){
        if(name_field.value.length < 11){
          state["check_length"] = true
          setState(state => ({...state}));
        }
        else { 
          state["check_length"] = false
          setState(state => ({...state}));
          
        }
    }
    

    
    if (missingField.length == 0 && !(name_field && state.check_length)){
      if (value == "Submit") {
        // add the filling time
        if (state["data"]["filling_time"]) {
          let start = state["data"]["filling_time"];
          let end = new Date();

          // to check for moinus time
          let days = end.getDay() - start.getDay()
          let hours = (end.getHours() - start.getHours()) +  (24 * days);
          let minutes = end.getMinutes() - start.getMinutes();
          if (minutes < 0) {
              minutes += 60;
              hours -= 1;
          }
          let final = hours + " hours & " + minutes + " minutes";
          state["data"]["filling_time"] = final;
          setState(state);
          console.log("final timer =", final);
        }

        //show loading text
        let lodaing_text = document.getElementById("loading_text");
        lodaing_text.classList.remove("hidden");

        e.target.disabled = true;
        await axios
          .post(url, state)
          .then((res) => {
            let reference = res.data;
            state[stateKey] = reference;
            console.log("api response ==", state[stateKey]);
            setState(state);

            console.log("finale state = ", state);
          })
          .catch((err) => {
            // what now?
            console.log(err);
          });
        link.click();
        console.log("route =", route);
        return null;
      } else link.click();
    } 
    else{
      if (missingField != 0)
      alert(
        "Please Fill up the following fields: \n " +
          missingField.toString() +
          "   "
          );        
      window.location.hash = "#page_title"
      return;
    }
  };

  return (
    <div>
      <Button value={value} onClick={handle_click} />
      <Link
        to={full_path}
        style={{ display: "none" }}
        name="rLink"
        onClick={onClick}
      ></Link>
    </div>
  );
};

// Here when button next and previous goes
export const Button = ({ onClick, value }) => {
  return (
    <button
      onClick={onClick}
      className="bg-orange-500 text-white focus:text-white focus:outline-none focus:bg-orange-700 hover:bg-orange-700 py-2 px-4 rounded req "
    >
      {value}
    </button>
  );
};

export const check_job_id = (state, setState, ignore_name=false, add_job=false) => {
  // the variable ignore_name is used to not make the first page keep doing an endless refresh loop
  // the add_job is used to know when to change the page becauase of a missing job_id and when to not

  let url = new URL(document.URL)
  let job_id = Number( url.searchParams.get("job_id") )
  if (!state.data.job_id){
    if (add_job && job_id){
      state.data.job_id = job_id
      setState(state)
    } else{
      if (job_id){
        document.location.href = `${url.origin}/personal?job_id=${job_id}`
      } else {
        document.location.href = url.origin
      }
      return
    }
  }
  if (!state.data.name && !ignore_name){
    if (job_id){
      document.location.href = `${url.origin}/personal?job_id=${job_id}`
    } else {
      document.location.href = url.origin
    }
  }
}
