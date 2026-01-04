export default function ChatList({chats}){
    return(
        <div>
            {chats.map((chat)=>(
                <p key={chat._id} className={`message ${chat.role}`}>
                    {/* <b>{chat.role}:</b>  */}
                    {chat.reply}</p>
                   
            ))}
        </div>
    )
}