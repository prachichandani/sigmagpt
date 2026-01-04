import {useState} from 'react'
export default function ChatInput({onsend,onclear,loading,onstop}){
    const [text,setText] = useState('');
    const handlesend=()=>{
         if(!text.trim())return;
         onsend(text);
         setText('');
    }
    return(
        <div className='input-form'>
            <input type="text" disabled={loading}   
            placeholder='type a message' value={text} 
            onChange={(e)=>{setText(e.target.value)}}/>
            {/* &nbsp; &nbsp; */}
            <button onClick={handlesend}  disabled={loading}    >Send</button>
            {/* &nbsp; &nbsp; */}
           <button onClick={onclear}  disabled={loading} >Clear</button>
            <button onClick={onstop}  disabled={!loading} >stop</button>
            
           
        </div>
    )
}