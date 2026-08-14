import {useState} from 'react'
export default function ChatInput({onsend,onclear,loading,onstop,useRag,onToggleRag}){
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
            <div className="rag-toggle">
                <label className="toggle-label">
                    <input
                        type="checkbox"
                        checked={useRag}
                        onChange={onToggleRag}
                        disabled={loading}
                    />
                    <span className="toggle-slider"></span>
                    <span className="toggle-text">RAG</span>
                </label>
            </div>
        </div>
    )
}