import { listenerCount } from "stream";
import {MouseEvent, useState} from "react"

interface Props {
    items: String[];
    heading: String;
    onSelectItem: (item: String) => void;

}
function ListGroup({items, heading, onSelectItem}: Props) {
    const [selectedIndex, setSelectedIndex] = useState(-1)


    return (<>
        <h1>{heading}</h1>
        {items.length == 0 ? <p>No item found</p> : null}
        <ul className="list-group"> 
        {items.map((item, index) => <li className= {selectedIndex == index ? 'list-group-item active' : 'list-group-item'} key={item} onClick={() => {setSelectedIndex(index); onSelectItem(item);}}>{item}</li>)}
        </ul>
    </>
    );
}

export default ListGroup;